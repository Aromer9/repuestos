"""
Agente OpenClaw — powered by OpenAI GPT-4o-mini (temporal)
SDK: openai (https://github.com/openai/openai-python)

El modelo recibe la solicitud de cotización y decide autónomamente:
  - Qué mensaje de confirmación enviar por WhatsApp
  - Con cuántos partners cotizar y cómo comunicarlo
  - Cómo actualizar el estado en MongoDB

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

MODEL = "gpt-4o-mini"     # Temporal: OpenAI (cambiar a claude-sonnet-4-5 cuando haya créditos Anthropic)
MAX_ITERATIONS = 10        # Seguridad: máximo de iteraciones del loop

# ─────────────────────────────────────────────────────────────
# Definición de herramientas (tools) para Claude
# ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp",
            "description": "Envía un mensaje de texto por WhatsApp al cliente.",
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
            "description": "Obtiene todos los proveedores/partners activos para cotizar el repuesto.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_inquiry",
            "description": "Actualiza el estado de la cotización en la base de datos al final del flujo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "quoted", "closed"]},
                    "agent_status": {"type": "string", "enum": ["processing", "quoted", "awaiting_manual", "no_partners", "error"]},
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
]


# ─────────────────────────────────────────────────────────────
# Ejecución de tools
# ─────────────────────────────────────────────────────────────

async def execute_tool(name: str, inputs: dict, inquiry: dict) -> str:
    db = get_db()

    if name == "send_whatsapp":
        ok = await send_text(inputs["phone"], inputs["message"])
        return "Mensaje enviado." if ok else "Mensaje en modo simulación (sin credenciales WA)."

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

    if name == "update_inquiry":
        await db.inquiries.update_one(
            {"_id": inquiry["_id"]},
            {"$set": {
                "status": inputs["status"],
                "agent_status": inputs["agent_status"],
                "agent_notes": inputs.get("agent_notes", ""),
                "agent_finished_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return f"Cotización actualizada: {inputs['status']} / {inputs['agent_status']}"

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

    return f"Tool desconocida: {name}"


# ─────────────────────────────────────────────────────────────
# Instrucciones del sistema
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres OpenClaw, el agente de cotización automática de ARGParts.
ARGParts es una empresa chilena especializada en repuestos para autos japoneses (dropshipping).

Tu personalidad: profesional, cercano, eficiente. Hablas español chileno.

## Flujo obligatorio al recibir una solicitud:

1. Consulta la memoria del cliente con get_memory para ver si tiene historial previo.

2. Envía un WhatsApp de confirmación al cliente con send_whatsapp. El mensaje debe:
   - Saludar por nombre
   - Confirmar marca, modelo, año y repuesto con *negrita*
   - Indicar que estás cotizando ahora mismo
   - Si es cliente recurrente, mencionarlo ("¡Qué bueno verte de nuevo!")
   - Firmar como "Equipo ARGParts 🚗"

3. Obtén los partners activos con get_active_partners.

4. Si NO hay partners:
   - Envía WhatsApp informando que un asesor lo contactará pronto
   - Actualiza con agent_status="no_partners"

5. Si HAY partners:
   - Envía WhatsApp indicando que estás consultando con N proveedores especializados
   - Actualiza con agent_status="awaiting_manual" (los precios se ingresan desde el panel admin)

6. Guarda en memoria el vehículo principal del cliente con save_memory.

7. Actualiza el estado final con update_inquiry.

## Reglas de formato para WhatsApp:
- Máximo 4 párrafos cortos
- Usa *negrita* para datos del vehículo y repuesto
- Emojis moderados (🚗 🔍 ✅ 📞)
- Nunca uses markdown con # o ** doble
"""


# ─────────────────────────────────────────────────────────────
# Agentic loop principal
# ─────────────────────────────────────────────────────────────

async def run(inquiry: dict) -> None:
    name      = inquiry.get("name", "cliente")
    phone     = inquiry.get("phone", "")
    brand     = inquiry.get("brand", "")
    model_car = inquiry.get("model", "")
    year      = inquiry.get("year", "")
    part      = inquiry.get("part_description", "")
    vin       = inquiry.get("vin") or "No proporcionado"

    logger.info(f"🤖 OpenClaw (GPT-4o-mini) iniciado — {name} | {brand} {model_car} {year}")

    db = get_db()
    await db.inquiries.update_one(
        {"_id": inquiry["_id"]},
        {"$set": {
            "agent_status": "processing",
            "agent_started_at": datetime.now(timezone.utc),
        }},
    )

    api_key = os.getenv("OPEN_AI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("⚠️  OPEN_AI_API_KEY no configurada — modo simulación")
        await _fallback_run(inquiry, db, name, phone, brand, model_car, year, part)
        return

    client = openai.AsyncOpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Nueva solicitud de cotización:\n\n"
                f"- Cliente: {name}\n"
                f"- Teléfono: {phone}\n"
                f"- Vehículo: {brand} {model_car} {year}\n"
                f"- Repuesto: {part}\n"
                f"- VIN: {vin}\n"
                f"- RUT: {inquiry.get('rut', '')}\n\n"
                f"Procede con el flujo completo."
            ),
        },
    ]

    # ── Agentic loop ──────────────────────────────────────────
    for iteration in range(MAX_ITERATIONS):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                tools=TOOLS,
                messages=messages,
                tool_choice="auto",
            )
        except Exception as e:
            logger.error(f"❌ Error llamando a OpenAI: {e}")
            await db.inquiries.update_one(
                {"_id": inquiry["_id"]},
                {"$set": {"agent_status": "error", "agent_error": str(e)}},
            )
            return

        choice = response.choices[0]
        assistant_msg = choice.message

        # Agregar respuesta al historial
        messages.append(assistant_msg.model_dump(exclude_unset=False, exclude_none=True))

        # ¿Terminó el agente?
        if choice.finish_reason == "stop":
            logger.info(f"✅ OpenClaw completó flujo en {iteration + 1} iteración(es)")
            break

        # ¿Quiere usar herramientas?
        if choice.finish_reason == "tool_calls" and assistant_msg.tool_calls:
            for tc in assistant_msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_input = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_input = {}
                logger.info(f"🔧 Tool: {tool_name} → {tool_input}")
                result = await execute_tool(tool_name, tool_input, inquiry)
                logger.info(f"   ↳ {result[:120]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        else:
            break

    # Guardar número de turnos para trazabilidad
    await db.inquiries.update_one(
        {"_id": inquiry["_id"]},
        {"$set": {"agent_conversation_turns": len(messages)}},
    )


# ─────────────────────────────────────────────────────────────
# Modo simulación (sin API key)
# ─────────────────────────────────────────────────────────────

async def _fallback_run(inquiry, db, name, phone, brand, model_car, year, part):
    if phone:
        msg = (
            f"👋 Hola *{name}*, somos *ARGParts*.\n\n"
            f"Recibimos tu solicitud de cotización:\n"
            f"• Vehículo: *{brand} {model_car} {year}*\n"
            f"• Repuesto: *{part}*\n\n"
            f"Estamos consultando con nuestros proveedores ahora mismo. "
            f"Te avisamos en breve con los precios. 🔍\n\n"
            f"Equipo ARGParts 🚗"
        )
        await send_text(phone, msg)

    await db.inquiries.update_one(
        {"_id": inquiry["_id"]},
        {"$set": {
            "agent_status": "awaiting_manual",
            "updated_at": datetime.now(timezone.utc),
        }},
    )
    logger.info(f"📬 Simulación completada para {inquiry.get('_id')}")
