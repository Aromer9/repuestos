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
            "description": "Consulta si algún proveedor ya respondió con precios para esta cotización. Devuelve nombre, estado, precio y respuesta de cada uno.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_partner_price",
            "description": (
                "Guarda el precio estructurado de un proveedor en partner_quotes. "
                "Llama esta tool cada vez que proceses la respuesta de un proveedor con datos de precio. "
                "Usa el telefono del proveedor para identificar el registro."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_phone": {"type": "string", "description": "Telefono del proveedor"},
                    "price_amount": {"type": "number", "description": "Precio en numeros (ej: 45000)"},
                    "price_currency": {"type": "string", "description": "Moneda, default CLP", "default": "CLP"},
                    "is_original": {"type": "boolean", "description": "True si es repuesto original, False si es alternativo, null si no se sabe"},
                    "summary": {"type": "string", "description": "Resumen breve de la oferta (ej: 'Original Toyota, stock inmediato, $45.000')"},
                },
                "required": ["partner_phone", "price_amount", "summary"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_draft_for_approval",
            "description": (
                "Guarda el borrador de cotizacion para aprobacion interna del admin. "
                "NO envia nada al cliente — solo prepara el borrador y notifica al admin. "
                "Llama esta tool cuando TODOS los proveedores hayan respondido y hayas analizado las ofertas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "proposed_message": {
                        "type": "string",
                        "description": (
                            "Mensaje completo que se enviaria al cliente si el admin aprueba. "
                            "Debe incluir las opciones de precio, indicar cual es la mejor y por que. "
                            "Tono natural, como si lo escribiera una persona del equipo ARGParts."
                        ),
                    },
                    "best_option_summary": {
                        "type": "string",
                        "description": "Resumen interno de 1-2 lineas con la mejor opcion y su precio (para que el admin entienda rapidamente).",
                    },
                },
                "required": ["proposed_message", "best_option_summary"],
            },
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
                "price_amount": pq.get("price_amount"),
                "price_currency": pq.get("price_currency", "CLP"),
                "is_original": pq.get("is_original"),
                "summary": pq.get("price_summary"),
                "response": pq.get("response"),
            })
        if not responses:
            return "No se han enviado solicitudes a proveedores aun."
        total = len(responses)
        responded = sum(1 for r in responses if r["status"] == "responded")
        return json.dumps({
            "total_partners": total,
            "responded": responded,
            "pending": total - responded,
            "all_responded": responded == total,
            "quotes": responses,
        }, ensure_ascii=False)

    if name == "save_partner_price":
        from app.agent.whatsapp import _clean_phone
        digits = _clean_phone(inputs["partner_phone"])
        now = datetime.now(timezone.utc)
        result = await db.partner_quotes.find_one_and_update(
            {
                "inquiry_id": inquiry_id,
                "partner_phone": {"$regex": digits[-9:]},
            },
            {"$set": {
                "price_amount": inputs["price_amount"],
                "price_currency": inputs.get("price_currency", "CLP"),
                "is_original": inputs.get("is_original"),
                "price_summary": inputs["summary"],
                "updated_at": now,
            }},
            return_document=True,
        )
        if result:
            return f"Precio guardado para {result['partner_name']}: ${inputs['price_amount']:,.0f} {inputs.get('price_currency','CLP')} — {inputs['summary']}"
        return "No se encontro el registro de este proveedor para esta cotizacion."

    if name == "submit_draft_for_approval":
        from app.database import settings
        now = datetime.now(timezone.utc)
        await db.inquiries.update_one(
            {"_id": inquiry_id},
            {"$set": {
                "agent_status": "awaiting_approval",
                "proposed_client_message": inputs["proposed_message"],
                "proposed_best_option": inputs["best_option_summary"],
                "agent_finished_at": now,
                "updated_at": now,
            }},
        )
        # Notificar al admin por WhatsApp
        admin_phone = settings.admin_phone
        if admin_phone:
            inq = inquiry
            client_name = inq.get("name", "un cliente")
            vehicle = f"{inq.get('brand','')} {inq.get('model','')} {inq.get('year','')}".strip()
            part = inq.get("part_description", "repuesto")
            admin_msg = (
                f"Cotizacion lista para revision 👆\n\n"
                f"*Cliente:* {client_name}\n"
                f"*Vehiculo:* {vehicle}\n"
                f"*Repuesto:* {part}\n\n"
                f"*Mejor opcion:* {inputs['best_option_summary']}\n\n"
                f"Entra al panel admin para aprobar o editar el mensaje antes de enviarselo al cliente."
            )
            await send_text(admin_phone, admin_msg)
        return f"Borrador guardado y admin notificado. agent_status=awaiting_approval."

    return f"Tool desconocida: {name}"


# ─────────────────────────────────────────────────────────────
# Instrucciones del sistema
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres el asistente de cotizaciones de ARGParts, empresa chilena de repuestos para autos japoneses.

Escribes en español chileno, de forma cercana y natural. Suenas como una persona del equipo, no como un bot ni un call center.

════════════════════════════════════════
FLUJO AL RECIBIR UNA SOLICITUD NUEVA
════════════════════════════════════════

PASO 1 — Historial del cliente
Llama get_memory con el telefono del cliente. Si ya compro antes, mencionalo calurosamente.

PASO 2 — Confirma al cliente por WhatsApp
Usa send_whatsapp. El tono debe ser:
  - Saluda por su nombre, de forma casual
  - Confirma en *negrita* el vehiculo y el repuesto
  - Dile que ya estas consultando con proveedores
  - Firma como "ARGParts"
  - Ejemplo: "Hola [Nombre]! Recibimos tu solicitud para el *[repuesto]* del *[marca modelo año]*, ya estamos viendo precios con nuestros proveedores. Te aviso en cuanto tenga novedades 🙌"

PASO 3 — Obtén proveedores activos
Llama get_active_partners.

PASO 4a — Sin proveedores activos:
  - Avisa al cliente que un asesor lo contactara pronto
  - Llama update_inquiry con agent_status="no_partners"

PASO 4b — Con proveedores activos:
  Llama send_quote_request_to_partners con un message_template que:
  - Empiece con "Hola {partner_name}!"
  - Suene como mensaje entre colegas del rubro
  - Incluya TODOS estos datos sin excepcion:
      * Marca, modelo y año del vehiculo
      * Descripcion completa del repuesto solicitado
      * VIN si el cliente lo proporciono
      * RUT del cliente
  - Pregunte por precio, disponibilidad y si es original o alternativo
  - Maximo 6 lineas, firma como "ARGParts"

  Ejemplo de message_template:
  "Hola {partner_name}! Te escribo de ARGParts 👋
Ando necesitando un *[repuesto exacto]* para un *[marca] [modelo] [año]*[, VIN: XXXX si aplica], RUT cliente: [RUT].
¿Tienes disponibilidad? ¿A cuanto quedaría? Si puedes avisar si es original o alternativo, mejor.
Gracias!
ARGParts"

  Luego llama update_inquiry con status="pending" y agent_status="awaiting_partners".

PASO 5 — Guarda vehiculo en memoria
Llama save_memory con key="vehiculo_principal" y marca+modelo+año como valor.

════════════════════════════════════════
FLUJO AL RECIBIR RESPUESTA DE PROVEEDOR
════════════════════════════════════════

IMPORTANTE: NUNCA envies la cotizacion directamente al cliente. El flujo es:
  1. Agradecer al proveedor
  2. Guardar el precio estructurado
  3. Revisar si faltan respuestas
  4. Cuando todos respondieron: preparar borrador y esperar aprobacion del admin

Paso a paso:

1. Agradece al proveedor por whatsapp (send_whatsapp), mensaje breve y cordial.
   Ejemplo: "Gracias [nombre]! Anotado todo, quedamos en contacto 👍"

2. Llama save_partner_price con:
   - partner_phone: el telefono desde donde respondio
   - price_amount: el precio en numeros (sin simbolos)
   - is_original: true/false segun lo que dijo el proveedor (null si no quedo claro)
   - summary: resumen de 1 linea con la oferta ("Original Toyota, stock inmediato, $45.000")

3. Llama check_partner_responses para ver cuantos han respondido.

4. Si aun faltan respuestas (all_responded = false): detente aqui, no hagas nada mas.

5. Si TODOS respondieron (all_responded = true):
   a. Analiza todas las cotizaciones y decide la mejor opcion (precio, originalidad, disponibilidad)
   b. Prepara dos textos:
      - proposed_message: el mensaje completo que se le enviaria al cliente si el admin aprueba.
        * Tono: natural, como si lo escribiera alguien del equipo
        * Incluye las opciones disponibles con precios
        * Indica cual es la mejor y por que
        * NO incluyas frases de aprobacion ni menciones al proceso interno
        * Ejemplo de tono: "Hola [Nombre]! Ya tenemos precios para el *[repuesto]*. 
          La mejor opcion que encontramos es con [proveedor], *$XX.000*, [original/alternativo], disponible de inmediato.
          Tambien hay una opcion alternativa con [proveedor2] a *$YY.000*.
          ¿Te acomoda? Quedamos a tu disposicion."
      - best_option_summary: resumen interno de 1-2 lineas para el admin
        * Ejemplo: "Mejor: Toyotoshi, original, $45.000 (stock). Alternativa: RepuestosCL, $28.000."
   c. Llama submit_draft_for_approval con esos dos textos.
   d. NO llames send_whatsapp al cliente — el admin aprobara antes.

════════════════════════════════════════
FLUJO AL RECIBIR MENSAJE DEL CLIENTE
════════════════════════════════════════

1. Responde de forma natural y util segun lo que pregunte.
2. Si pregunta por el estado: llama check_partner_responses y cuentale cuantos respondieron.
3. Si la cotizacion ya esta en "awaiting_approval": dile que el equipo ya tiene los precios y
   que en breve le enviaran la cotizacion (sin mencionar el proceso de aprobacion interno).
4. Si confirma que quiere una opcion: llama update_inquiry con status="closed".

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
