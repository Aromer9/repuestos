"""
Servicio de WhatsApp via Meta Cloud API.
Documentación: https://developers.facebook.com/docs/whatsapp/cloud-api/messages
"""
import httpx
import logging
from app.database import settings

logger = logging.getLogger("openclaw.whatsapp")

WA_API_URL = "https://graph.facebook.com/v19.0"


def _clean_phone(phone: str) -> str:
    """Normaliza el número: solo dígitos, agrega 56 si es chileno sin código."""
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 9 and not digits.startswith("56"):
        digits = "56" + digits
    return digits


async def send_text(to: str, message: str) -> bool:
    """Envía un mensaje de texto libre por WhatsApp."""
    if not settings.whatsapp_token or not settings.whatsapp_phone_id:
        logger.warning("WhatsApp no configurado — mensaje no enviado.")
        logger.info(f"[SIMULADO → {to}]: {message}")
        return False

    phone = _clean_phone(to)
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message},
    }
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            res = await client.post(
                f"{WA_API_URL}/{settings.whatsapp_phone_id}/messages",
                json=payload,
                headers=headers,
            )
            if res.status_code == 200:
                logger.info(f"✅ WhatsApp enviado a {phone}")
                return True
            else:
                logger.error(f"❌ Error WhatsApp {res.status_code}: {res.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Excepción WhatsApp: {e}")
            return False
