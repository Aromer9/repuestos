"""
Webhook de WhatsApp via Evolution API (open source).
Docs: https://doc.evolution-api.com/v2/webhooks

Evolution API envia un POST con el siguiente payload:
{
  "event": "messages.upsert",
  "instance": "argparts",
  "data": {
    "key": { "remoteJid": "56912345678@s.whatsapp.net", "fromMe": false },
    "message": { "conversation": "Hola, precio?" },
    "messageType": "conversation",
    ...
  }
}

Cuando llega un mensaje, identifica si proviene de un cliente o proveedor,
busca la cotizacion asociada, y dispara el agente OpenClaw para responder.
"""
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Request

from app.database import get_db, settings

logger = logging.getLogger("openclaw.webhook")
router = APIRouter(prefix="/webhook", tags=["Webhook WhatsApp"])


def _normalize_phone(phone: str) -> str:
    """Extrae solo digitos de un numero (remueve @s.whatsapp.net, +, espacios, etc)."""
    return "".join(c for c in phone if c.isdigit())


def _extract_phone_from_jid(jid: str) -> str:
    """Convierte '56912345678@s.whatsapp.net' -> '56912345678'."""
    return jid.split("@")[0] if "@" in jid else jid


def _extract_text(data: dict) -> str:
    """
    Extrae el texto del mensaje desde el payload de Evolution API.
    Soporta conversation, extendedTextMessage, imageMessage (caption), etc.
    """
    msg = data.get("message", {})
    return (
        msg.get("conversation")
        or msg.get("extendedTextMessage", {}).get("text")
        or msg.get("imageMessage", {}).get("caption")
        or msg.get("videoMessage", {}).get("caption")
        or ""
    )


async def _find_inquiry_for_number(db, phone: str):
    """Busca la cotizacion activa mas reciente asociada a este numero."""
    digits = _normalize_phone(phone)

    inquiry = await db.inquiries.find_one(
        {
            "phone": {"$regex": digits[-9:]},
            "status": {"$in": ["pending", "quoted"]},
        },
        sort=[("created_at", -1)],
    )
    if inquiry:
        return inquiry, "client"

    partner_quote = await db.partner_quotes.find_one(
        {
            "partner_phone": {"$regex": digits[-9:]},
            "status": "waiting",
        },
        sort=[("sent_at", -1)],
    )
    if partner_quote:
        inquiry = await db.inquiries.find_one({"_id": partner_quote["inquiry_id"]})
        if inquiry:
            return inquiry, "partner"

    return None, None


def _run_agent_reply(inquiry: dict, extra_messages: list[dict]) -> None:
    from app.agent import openclaw
    try:
        asyncio.run(openclaw.run(inquiry, extra_messages=extra_messages))
    except Exception as e:
        logger.error(f"Error en agente OpenClaw (reply): {e}")


async def _handle_partner_response(db, phone: str, text: str):
    """Registra la respuesta del proveedor en partner_quotes."""
    digits = _normalize_phone(phone)
    now = datetime.now(timezone.utc)

    result = await db.partner_quotes.find_one_and_update(
        {
            "partner_phone": {"$regex": digits[-9:]},
            "status": "waiting",
        },
        {"$set": {
            "status": "responded",
            "response": text,
            "responded_at": now,
        }},
        sort=[("sent_at", -1)],
        return_document=True,
    )
    if result:
        logger.info(
            f"Respuesta de proveedor {result['partner_name']} registrada "
            f"para inquiry {result['inquiry_id']}"
        )
    return result


@router.post("/whatsapp", summary="Eventos entrantes de Evolution API")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    """
    Recibe eventos de Evolution API. Procesa mensajes entrantes de clientes
    y proveedores, y dispara el agente para responder.
    """
    try:
        body = await request.json()

        event = body.get("event", "")

        # Solo procesar mensajes entrantes reales
        if event not in ("messages.upsert", "messages.update"):
            return {"status": "ignored", "event": event}

        data = body.get("data", {})

        # Ignorar mensajes enviados por nosotros mismos
        key = data.get("key", {})
        if key.get("fromMe", False):
            return {"status": "ignored", "reason": "outbound"}

        jid = key.get("remoteJid", "")
        if not jid or "status" in jid:
            return {"status": "ignored", "reason": "no_jid"}

        from_number = _extract_phone_from_jid(jid)
        text = _extract_text(data)

        if not text:
            return {"status": "ignored", "reason": "no_text"}

        logger.info(f"WhatsApp recibido de {from_number}: '{text[:80]}'")

        db = get_db()
        await db.message_log.insert_one({
            "from": from_number,
            "direction": "inbound",
            "event": event,
            "text": text,
            "raw": data,
            "received_at": datetime.now(timezone.utc),
        })

        inquiry, sender_type = await _find_inquiry_for_number(db, from_number)

        if not inquiry:
            logger.info(f"No se encontro cotizacion activa para {from_number}")
            return {"status": "ok", "action": "no_inquiry"}

        if sender_type == "partner":
            await _handle_partner_response(db, from_number, text)
            extra = [{
                "role": "user",
                "content": (
                    f"Respuesta de proveedor (telefono {from_number}):\n\n"
                    f'"{text}"\n\n'
                    f"Procesa esta respuesta segun el flujo de respuesta de proveedor."
                ),
            }]
        else:
            extra = [{
                "role": "user",
                "content": (
                    f"Mensaje del cliente (telefono {from_number}):\n\n"
                    f'"{text}"\n\n'
                    f"Responde al cliente segun el flujo de respuesta de cliente."
                ),
            }]

        background_tasks.add_task(_run_agent_reply, dict(inquiry), extra)
        logger.info(
            f"Agente encolado para inquiry {inquiry['_id']} (sender: {sender_type})"
        )

    except Exception as e:
        logger.error(f"Error procesando webhook Evolution API: {e}")

    return {"status": "ok"}
