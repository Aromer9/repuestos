"""
Agente OpenClaw — powered by OpenAI GPT-4o-mini (temporal)
SDK: openai (https://github.com/openai/openai-python)

El modelo recibe la solicitud de cotización y decide autónomamente:
  - Confirmar al cliente por WhatsApp
  - Contactar a cada proveedor activo para pedir precio
  - Procesar respuestas y consolidar cotizaciones
  - Actualizar el estado en MongoDB

Agentic loop: GPT llama tools → recibe resultados → decide si sigue o termina.
"""
import json
import logging
import os
from datetime import datetime, timezone

import openai

from app.agent.whatsapp import send_text
from app.database import get_db

logger = logging.getLogger("openclaw")

MODEL = "gpt-4o-mini"
MAX_ITERATIONS = 15

# ─────────────────────────────────────────────────────────────
# Definición de herramientas (tools)
# ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp",
            "description": "Envía un mensaje de texto por WhatsApp a UN número (cliente o proveedor).",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Número de teléfono (ej: +56912345678)"},
                    "message": {"type": "string", "description": "Texto del mensaje. Puedes usar *negrita* y emojis."},
                },
                "required": ["phone", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_partners",
            "description": "Obtiene todos los proveedores/partners activos con su teléfono para contactarlos.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_quote_request_to_partners",
            "description": (
                "Envía la solicitud de cotización por WhatsApp a TODOS los proveedores activos. "
                "Usa {partner_name} en el mensaje como placeholder — la tool lo reemplaza con el nombre "
                "real de cada proveedor antes de enviar, personalizando cada mensaje. "
                "Registra cada envío en la colección partner_quotes para rastrear respuestas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message_template": {
                        "type": "string",
                        "description": (
                            "Plantilla del mensaje para los proveedores. "
                            "Usa {partner_name} donde quieras poner el nombre del proveedor. "
                            "Debe incluir TODOS los datos: marca, modelo, año, repuesto, VIN si existe. "
                            "Tono: cálido, natural, como si fuera un mensaje entre colegas."
                        ),
                    },
                },
                "required": ["message_template"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_inquiry",
            "description": "Actualiza el estado de la cotización en la base de datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "quoted", "closed"]},
                    "agent_status": {
                        "type": "string",
                        "enum": [
                            "processing", "awaiting_partners", "quoted",
                            "awaiting_manual", "no_partners", "error",
                        ],
                    },
                    "agent_notes": {"type": "string", "description": "Notas internas del agente"},
                },
                "required": ["status", "agent_status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Guarda información del cliente en MongoDB para futuros contactos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string"},
                    "key": {"type": "string", "description": "Ej: 'vehiculo_principal'"},
                    "value": {"type": "string"},
                },
                "required": ["phone", "key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory",
            "description": "Recupera el historial guardado de un cliente por su teléfono.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string"},
                },
                "required": ["phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_partner_responses",
            "description": "Consulta si algún proveedor ya respondió con precios para esta cotización.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ─────────────────────────────────────────────────────────────
# Ejecución de tools
# ─────────────────────────────────────────────────────────────

async def execute_tool(name: str, inputs: dict, inquiry: dict) -> str:
    db = get_db()
    inquiry_id = inquiry["_id"]

    if name == "send_whatsapp":
        ok = await send_text(inputs["phone"], inputs["message"])
        return "Mensaje enviado." if ok else "Mensaje en modo simulacion (sin credenciales WA)."

    if name == "get_active_partners":
        partners = []
        async for p in db.partners.find({"active": True}):
            partners.append({
                "name": p["name"],
                "brand": p["brand"],
                "phone": p["phone"],
                "address": p["address"],
                "notes": p.get("notes", ""),
            })
        if not partners:
            return "No hay partners activos registrados."
        return json.dumps(partners, ensure_ascii=False)

    if name == "send_quote_request_to_partners":
        template = inputs.get("message_template", inputs.get("message", ""))

        partners = []
        async for p in db.partners.find({"active": True}):
            partners.append(p)

        if not partners:
            return "No hay proveedores activos registrados en el sistema."

        results = []
        now = datetime.now(timezone.utc)
        for p in partners:
            # Personalizar el mensaje con el nombre real del proveedor
            personalized = template.replace("{partner_name}", p["name"])
            ok = await send_text(p["phone"], personalized)
            await db.partner_quotes.insert_one({
                "inquiry_id": inquiry_id,
                "partner_id": p["_id"],
                "partner_name": p["name"],
                "partner_phone": p["phone"],
                "partner_brand": p["brand"],
                "message_sent": personalized,
                "sent_at": now,
                "status": "waiting",
                "response": None,
                "price": None,
                "responded_at": None,
            })
            status_txt = "enviado" if ok else "simulado"
            results.append(f"{p['name']} ({p['phone']}): {status_txt}")

        await db.inquiries.update_one(
            {"_id": inquiry_id},
            {"$set": {
                "partners_contacted": len(partners),
                "updated_at": now,
            }},
        )
        return f"Mensaje enviado a {len(partners)} proveedor(es):\n" + "\n".join(results)

    if name == "update_inquiry":
        await db.inquiries.update_one(
            {"_id": inquiry_id},
            {"$set": {
                "status": inputs["status"],
                "agent_status": inputs["agent_status"],
                "agent_notes": inputs.get("agent_notes", ""),
                "agent_finished_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return f"Cotizacion actualizada: {inputs['status']} / {inputs['agent_status']}"

    if name == "save_memory":
        await db.client_memory.update_one(
            {"phone": inputs["phone"]},
            {"$set": {
                f"data.{inputs['key']}": inputs["value"],
                "updated_at": datetime.now(timezone.utc),
            }},
            upsert=True,
        )
        return f"Memoria guardada: {inputs['key']} = {inputs['value']}"

    if name == "get_memory":
        doc = await db.client_memory.find_one({"phone": inputs["phone"]})
        if not doc:
            return "Sin historial previo para este cliente."
        return json.dumps(doc.get("data", {}), ensure_ascii=False)

    if name == "check_partner_responses":
        responses = []
        async for pq in db.partner_quotes.find({"inquiry_id": inquiry_id}):
            responses.append({
                "partner": pq["partner_name"],
                "status": pq["status"],
                "price": pq.get("price"),
                "response": pq.get("response"),
            })
        if not responses:
            return "No se han enviado solicitudes a proveedores aun."
        return json.dumps(responses, ensure_ascii=False)

    return f"Tool desconocida: {name}"


# ─────────────────────────────────────────────────────────────
# Instrucciones del sistema
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres el asistente de cotizaciones de ARGParts, una empresa chilena de repuestos para autos japoneses.

Tu nombre no importa — lo que importa es que suenes como una persona real, no como un bot. Escribes en español chileno, de forma cercana y natural. Nada de respuestas de call center.

════════════════════════════════════════
FLUJO AL RECIBIR UNA SOLICITUD NUEVA
════════════════════════════════════════

PASO 1 — Consulta si el cliente tiene historial
Llama get_memory con el telefono del cliente. Si ya compro antes, mencionalo calurosamente.

PASO 2 — Escribe al cliente confirmando su solicitud
Usa send_whatsapp. El mensaje debe sonar como lo escribiria una persona real:
  - Saluda por su nombre, de forma casual
  - Confirma el vehiculo y repuesto que pidio (en *negrita*)
  - Dile que ya estas consultando con tus proveedores
  - Firmalo como "ARGParts"

Ejemplo de tono correcto:
"Hola [Nombre]! Recibimos tu solicitud para el *[repuesto]* del *[marca modelo año]*, ya estamos consultando con nuestros proveedores ahora mismo. En cuanto tengamos precios te avisamos 🙌"

Ejemplo de tono INCORRECTO (evitar):
"Estimado cliente, hemos recibido su solicitud de cotización N°XXX..."

PASO 3 — Obtén los proveedores activos
Llama get_active_partners. Esto te entrega la lista completa con nombre, marca, telefono y notas de cada uno.

PASO 4a — Si NO hay proveedores activos:
  - Escribe al cliente que un asesor lo contactara pronto
  - Llama update_inquiry con agent_status="no_partners"

PASO 4b — Si HAY proveedores activos:
  Llama send_quote_request_to_partners con una message_template que:

  - Empiece con "Hola {partner_name}!" (la tool reemplaza {partner_name} con el nombre real)
  - Suene como si lo escribiera un colega del rubro, no un sistema automatizado
  - Incluya TODOS estos datos sin excepcion:
      * Marca del vehiculo
      * Modelo del vehiculo
      * Año del vehiculo
      * Descripcion completa del repuesto que pidio el cliente
      * VIN (si el cliente lo proporciono)
      * RUT del cliente (util para cotizaciones formales)
  - Pregunte por precio, disponibilidad y si es original o alternativo
  - Sea breve (maximo 6 lineas)
  - Firme como "ARGParts"

  Ejemplo de message_template correcto:
  "Hola {partner_name}! Te escribo de ARGParts 👋

Ando buscando un *[repuesto exacto]* para un *[marca] [modelo] [año]*[, VIN: XXXX si aplica].

¿Tienes disponibilidad? ¿A cuanto estaría? Si puedes indicar si es original o alternativo mejor aun.

Gracias!
ARGParts"

  Luego escribe al cliente avisandole cuantos proveedores estas consultando.
  Llama update_inquiry con agent_status="awaiting_partners".

PASO 5 — Guarda el vehiculo del cliente en memoria
Llama save_memory con key="vehiculo_principal" y el valor con marca+modelo+año.

PASO 6 — Actualiza la cotizacion
Llama update_inquiry con status="pending" y agent_status="awaiting_partners".

════════════════════════════════════════
FLUJO AL RECIBIR RESPUESTA DE PROVEEDOR
════════════════════════════════════════

1. Agradece al proveedor brevemente por whatsapp (send_whatsapp).
2. Llama check_partner_responses para ver cuantos han respondido.
3. Si TODOS respondieron:
   - Escribe al cliente un resumen claro con las opciones y precios recibidos
   - Preguntale cual prefiere
   - Llama update_inquiry con agent_status="quoted"
4. Si aun faltan respuestas, no hagas nada mas — espera.

════════════════════════════════════════
FLUJO AL RECIBIR MENSAJE DEL CLIENTE
════════════════════════════════════════

1. Responde de forma natural y util segun lo que pregunte.
2. Si pregunta por el estado: llama check_partner_responses y cuéntale cuántos respondieron.
3. Si confirma que quiere una opcion: llama update_inquiry con status="closed".

════════════════════════════════════════
REGLAS DE FORMATO WHATSAPP
════════════════════════════════════════
- Usa *negrita* para datos clave (repuesto, vehiculo, precios)
- Emojis con moderacion (1-2 por mensaje maximo)
- Parrafos cortos — maximo 5 lineas por mensaje
- NUNCA uses ## ni ** doble ni listas con guiones en secuencia larga
- Escribe como persona, no como sistema
"""


# ─────────────────────────────────────────────────────────────
# Agentic loop principal
# ─────────────────────────────────────────────────────────────

async def run(inquiry: dict, extra_messages: list[dict] | None = None) -> None:
    """
    Ejecuta el agente. Si extra_messages viene vacío, es una solicitud nueva.
    Si tiene mensajes, es una continuación (respuesta de proveedor o cliente).
    """
    name      = inquiry.get("name", "cliente")
    phone     = inquiry.get("phone", "")
    brand     = inquiry.get("brand", "")
    model_car = inquiry.get("model", "")
    year      = inquiry.get("year", "")
    part      = inquiry.get("part_description", "")
    vin       = inquiry.get("vin") or "No proporcionado"

    db = get_db()
    is_new = extra_messages is None

    if is_new:
        logger.info(f"OpenClaw iniciado — {name} | {brand} {model_car} {year}")
        await db.inquiries.update_one(
            {"_id": inquiry["_id"]},
            {"$set": {
                "agent_status": "processing",
                "agent_started_at": datetime.now(timezone.utc),
            }},
        )

    api_key = os.getenv("OPEN_AI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPEN_AI_API_KEY no configurada — modo simulacion")
        if is_new:
            await _fallback_run(inquiry, db, name, phone, brand, model_car, year, part)
        return

    client = openai.AsyncOpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if is_new:
        messages.append({
            "role": "user",
            "content": (
                f"Nueva solicitud de cotizacion:\n\n"
                f"- Cliente: {name}\n"
                f"- Telefono: {phone}\n"
                f"- Vehiculo: {brand} {model_car} {year}\n"
                f"- Repuesto: {part}\n"
                f"- VIN: {vin}\n"
                f"- RUT: {inquiry.get('rut', '')}\n\n"
                f"Procede con el flujo completo."
            ),
        })
    else:
        context = (
            f"Contexto de la cotizacion:\n"
            f"- Cliente: {name} ({phone})\n"
            f"- Vehiculo: {brand} {model_car} {year}\n"
            f"- Repuesto: {part}\n\n"
        )
        for em in extra_messages:
            em["content"] = context + em["content"]
        messages.extend(extra_messages)

    for iteration in range(MAX_ITERATIONS):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                tools=TOOLS,
                messages=messages,
                tool_choice="auto",
            )
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}")
            await db.inquiries.update_one(
                {"_id": inquiry["_id"]},
                {"$set": {"agent_status": "error", "agent_error": str(e)}},
            )
            return

        choice = response.choices[0]
        assistant_msg = choice.message
        messages.append(assistant_msg.model_dump(exclude_unset=False, exclude_none=True))

        if choice.finish_reason == "stop":
            logger.info(f"OpenClaw completo en {iteration + 1} iteracion(es)")
            break

        if choice.finish_reason == "tool_calls" and assistant_msg.tool_calls:
            for tc in assistant_msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_input = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_input = {}
                logger.info(f"Tool: {tool_name} -> {tool_input}")
                result = await execute_tool(tool_name, tool_input, inquiry)
                logger.info(f"   -> {result[:120]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        else:
            break

    await db.inquiries.update_one(
        {"_id": inquiry["_id"]},
        {"$set": {"agent_conversation_turns": len(messages)}},
    )


# ─────────────────────────────────────────────────────────────
# Modo simulacion (sin API key)
# ─────────────────────────────────────────────────────────────

async def _fallback_run(inquiry, db, name, phone, brand, model_car, year, part):
    now = datetime.now(timezone.utc)
    vin = inquiry.get("vin") or None
    rut = inquiry.get("rut", "")

    # Mensaje al cliente
    if phone:
        msg = (
            f"Hola {name}! Recibimos tu solicitud para el *{part}* "
            f"del *{brand} {model_car} {year}* 👌\n\n"
            f"Ya estamos consultando con nuestros proveedores ahora mismo. "
            f"En cuanto tengamos precios te avisamos.\n\n"
            f"ARGParts"
        )
        await send_text(phone, msg)

    # Mensaje a cada partner personalizado
    partners = []
    async for p in db.partners.find({"active": True}):
        partners.append(p)

    if partners:
        vin_line = f"\nVIN: {vin}" if vin else ""
        for p in partners:
            partner_msg = (
                f"Hola {p['name']}! Te escribo de ARGParts 👋\n\n"
                f"Ando buscando un *{part}* para un *{brand} {model_car} {year}*{vin_line}.\n\n"
                f"Tienes disponibilidad? A cuanto estaria? "
                f"Si puedes indicar si es original o alternativo mejor aun.\n\n"
                f"Gracias!\nARGParts"
            )
            await send_text(p["phone"], partner_msg)
            await db.partner_quotes.insert_one({
                "inquiry_id": inquiry["_id"],
                "partner_id": p["_id"],
                "partner_name": p["name"],
                "partner_phone": p["phone"],
                "partner_brand": p["brand"],
                "message_sent": partner_msg,
                "sent_at": now,
                "status": "waiting",
                "response": None,
                "price": None,
                "responded_at": None,
            })

    agent_status = "awaiting_partners" if partners else "no_partners"
    await db.inquiries.update_one(
        {"_id": inquiry["_id"]},
        {"$set": {
            "agent_status": agent_status,
            "partners_contacted": len(partners),
            "updated_at": now,
        }},
    )
    logger.info(f"Simulacion completada — {len(partners)} proveedores contactados")
