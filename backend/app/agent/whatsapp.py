"""
Servicio de WhatsApp via Evolution API (open source).
Docs: https://doc.evolution-api.com/v2/api-reference/message-controller/send-text

Cada mensaje enviado se registra en la coleccion message_log para trazabilidad.
Si las variables de entorno no estan configuradas opera en modo simulacion.
"""
import httpx
import logging
from datetime import datetime, timezone

from app.database import get_db, settings

logger = logging.getLogger("openclaw.whatsapp")


def _clean_phone(phone: str) -> str:
    """
    Normaliza el numero para Evolution API: solo digitos, con codigo de pais.
    Ejemplos: '912345678' -> '56912345678', '+56912345678' -> '56912345678'
    """
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 9 and not digits.startswith("56"):
        digits = "56" + digits
    return digits


async def _log_outbound(to: str, message: str, status: str):
    try:
        db = get_db()
        await db.message_log.insert_one({
            "to": to,
            "direction": "outbound",
            "type": "text",
            "text": message,
            "status": status,
            "sent_at": datetime.now(timezone.utc),
        })
    except Exception:
        pass


async def send_text(to: str, message: str) -> bool:
    """Envia un mensaje de texto libre por WhatsApp via Evolution API."""
    if not settings.evolution_api_url or not settings.evolution_instance:
        logger.warning(f"Evolution API no configurada — mensaje simulado a {to}")
        logger.info(f"[SIMULADO -> {to}]: {message}")
        await _log_outbound(to, message, "simulated")
        return False

    phone = _clean_phone(to)
    url = (
        f"{settings.evolution_api_url.rstrip('/')}"
        f"/message/sendText/{settings.evolution_instance}"
    )
    payload = {
        "number": phone,
        "text": message,
    }
    headers = {
        "apikey": settings.evolution_api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code in (200, 201):
                logger.info(f"WhatsApp enviado a {phone}")
                await _log_outbound(phone, message, "sent")
                return True
            else:
                logger.error(f"Error Evolution API {res.status_code}: {res.text}")
                await _log_outbound(phone, message, f"error_{res.status_code}")
                return False
        except Exception as e:
            logger.error(f"Excepcion Evolution API: {e}")
            await _log_outbound(phone, message, "exception")
            return False
