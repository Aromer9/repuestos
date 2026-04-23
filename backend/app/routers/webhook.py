"""
Webhook de WhatsApp (Meta Cloud API).

Meta requiere un endpoint GET para verificar el webhook y
un endpoint POST para recibir eventos (mensajes entrantes).

Documentación: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
"""
import logging
from fastapi import APIRouter, HTTPException, Request, Response
from app.database import settings

logger = logging.getLogger("openclaw.webhook")
router = APIRouter(prefix="/webhook", tags=["Webhook WhatsApp"])


@router.get("/whatsapp", summary="Verificación de webhook Meta")
async def verify_webhook(request: Request):
    """Meta llama a este endpoint para verificar que el servidor es válido."""
    params = dict(request.query_params)
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("✅ Webhook de WhatsApp verificado por Meta")
        return Response(content=challenge, media_type="text/plain")

    logger.warning("❌ Token de verificación incorrecto")
    raise HTTPException(status_code=403, detail="Token inválido")


@router.post("/whatsapp", summary="Eventos entrantes de WhatsApp")
async def receive_whatsapp(request: Request):
    """
    Recibe mensajes y eventos de WhatsApp enviados por Meta.
    Por ahora los registra en logs. En el futuro aquí OpenClaw
    puede reaccionar a respuestas del cliente (ej: confirmar opción 1).
    """
    try:
        body = await request.json()
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        messages = value.get("messages", [])
        for msg in messages:
            from_number = msg.get("from", "desconocido")
            msg_type    = msg.get("type", "")
            text        = msg.get("text", {}).get("body", "") if msg_type == "text" else ""

            logger.info(f"📨 WhatsApp recibido de {from_number}: '{text}'")

            # TODO: aquí OpenClaw puede responder automáticamente
            # según el contenido del mensaje (ej: "1" → confirmar primera opción)

    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")

    # Meta requiere siempre un 200 OK inmediato
    return {"status": "ok"}
