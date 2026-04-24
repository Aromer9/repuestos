import logging
from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import InquiryCreate, InquiryResponse, PartnerQuoteResponse

logger = logging.getLogger("argparts.inquiries")

router = APIRouter(prefix="/inquiries", tags=["Cotizaciones"])


def serialize_inquiry(doc: dict) -> InquiryResponse:
    doc["id"] = str(doc["_id"])
    return InquiryResponse(**doc)


async def _run_agent(inquiry: dict) -> None:
    """
    Ejecuta OpenClaw en el mismo event loop que FastAPI.
    No usar asyncio.run() aqui: Motor y httpx comparten el loop del servidor
    y si no, falla con 'Future attached to a different loop'.
    """
    from app.agent import openclaw
    try:
        await openclaw.run(inquiry)
    except Exception as e:
        logger.error(f"Error en agente OpenClaw: {e}", exc_info=True)


@router.post(
    "/",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cotización (público)",
)
async def create_inquiry(payload: InquiryCreate, background_tasks: BackgroundTasks):
    """Endpoint público: guarda la cotización y dispara el agente OpenClaw."""
    db = get_db()
    doc = payload.model_dump()
    now = datetime.now(timezone.utc)
    doc["status"] = "pending"
    doc["agent_status"] = "queued"
    doc["created_at"] = now
    doc["updated_at"] = now

    result = await db.inquiries.insert_one(doc)
    created = await db.inquiries.find_one({"_id": result.inserted_id})

    if not created:
        raise HTTPException(status_code=500, detail="Error al guardar la cotización")

    # Disparar agente en background sin bloquear la respuesta al cliente
    background_tasks.add_task(_run_agent, dict(created))
    logger.info(f"🚀 Agente OpenClaw encolado para inquiry {result.inserted_id}")

    return serialize_inquiry(created)


@router.get(
    "/",
    response_model=list[InquiryResponse],
    summary="Listar cotizaciones (admin)",
)
async def list_inquiries(
    limit: int = 100,
    skip: int = 0,
    status_filter: str | None = None,
    _: Annotated[dict, Depends(require_admin)] = None,
):
    db = get_db()
    query = {}
    if status_filter:
        query["status"] = status_filter
    cursor = db.inquiries.find(query).sort("created_at", -1).skip(skip).limit(limit)
    inquiries = []
    async for doc in cursor:
        inquiries.append(serialize_inquiry(doc))
    return inquiries


@router.get(
    "/{inquiry_id}",
    response_model=InquiryResponse,
    summary="Obtener cotización (admin)",
)
async def get_inquiry(
    inquiry_id: str,
    _: Annotated[dict, Depends(require_admin)] = None,
):
    if not ObjectId.is_valid(inquiry_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_db()
    doc = await db.inquiries.find_one({"_id": ObjectId(inquiry_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    return serialize_inquiry(doc)


@router.patch(
    "/{inquiry_id}/status",
    response_model=InquiryResponse,
    summary="Cambiar estado (admin)",
)
async def update_status(
    inquiry_id: str,
    new_status: str,
    _: Annotated[dict, Depends(require_admin)] = None,
):
    allowed = {"pending", "quoted", "closed"}
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Estado debe ser uno de: {allowed}")
    if not ObjectId.is_valid(inquiry_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_db()
    result = await db.inquiries.find_one_and_update(
        {"_id": ObjectId(inquiry_id)},
        {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    return serialize_inquiry(result)


@router.delete(
    "/{inquiry_id}",
    status_code=204,
    summary="Eliminar cotización (admin)",
)
async def delete_inquiry(
    inquiry_id: str,
    _: Annotated[dict, Depends(require_admin)] = None,
):
    if not ObjectId.is_valid(inquiry_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_db()
    result = await db.inquiries.delete_one({"_id": ObjectId(inquiry_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")


# ─────────────────────────────────────────────────────────────
# Endpoints de aprobacion interna
# ─────────────────────────────────────────────────────────────

@router.get(
    "/{inquiry_id}/quotes",
    response_model=list[PartnerQuoteResponse],
    summary="Obtener cotizaciones de proveedores (admin)",
)
async def get_partner_quotes(
    inquiry_id: str,
    _: Annotated[dict, Depends(require_admin)] = None,
):
    if not ObjectId.is_valid(inquiry_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_db()
    quotes = []
    async for pq in db.partner_quotes.find({"inquiry_id": ObjectId(inquiry_id)}):
        pq["id"] = str(pq["_id"])
        quotes.append(PartnerQuoteResponse(**pq))
    return quotes


@router.post(
    "/{inquiry_id}/approve",
    response_model=InquiryResponse,
    summary="Aprobar cotización y enviar al cliente (admin)",
)
async def approve_inquiry(
    inquiry_id: str,
    body: dict = Body(default={}),
    current_user: Annotated[dict, Depends(require_admin)] = None,
):
    """
    Aprueba el borrador de la cotizacion.
    Si se envia `message` en el body, ese texto reemplaza el borrador generado por la IA.
    """
    if not ObjectId.is_valid(inquiry_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_db()
    inquiry = await db.inquiries.find_one({"_id": ObjectId(inquiry_id)})
    if not inquiry:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    if inquiry.get("agent_status") != "awaiting_approval":
        raise HTTPException(
            status_code=400,
            detail="La cotización no está pendiente de aprobación",
        )

    # Usar mensaje personalizado si viene en el body, sino el borrador de la IA
    final_message = body.get("message") or inquiry.get("proposed_client_message") or ""
    if not final_message:
        raise HTTPException(status_code=400, detail="No hay mensaje para enviar al cliente")

    # Enviar WhatsApp al cliente
    from app.agent.whatsapp import send_text
    client_phone = inquiry.get("phone", "")
    ok = await send_text(client_phone, final_message)
    if not ok:
        logger.warning(f"WhatsApp al cliente {client_phone} no enviado (modo simulacion)")

    now = datetime.now(timezone.utc)
    admin_username = current_user.get("username", "admin") if current_user else "admin"

    updated = await db.inquiries.find_one_and_update(
        {"_id": ObjectId(inquiry_id)},
        {"$set": {
            "status": "quoted",
            "agent_status": "quoted",
            "approved_at": now,
            "approved_by": admin_username,
            "updated_at": now,
        }},
        return_document=True,
    )
    logger.info(f"Cotizacion {inquiry_id} aprobada por {admin_username}")
    return serialize_inquiry(updated)


@router.post(
    "/{inquiry_id}/reject",
    response_model=InquiryResponse,
    summary="Rechazar borrador y volver a espera de proveedores (admin)",
)
async def reject_inquiry(
    inquiry_id: str,
    _: Annotated[dict, Depends(require_admin)] = None,
):
    if not ObjectId.is_valid(inquiry_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_db()
    now = datetime.now(timezone.utc)
    updated = await db.inquiries.find_one_and_update(
        {"_id": ObjectId(inquiry_id)},
        {"$set": {
            "agent_status": "awaiting_partners",
            "proposed_client_message": None,
            "proposed_best_option": None,
            "updated_at": now,
        }},
        return_document=True,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    logger.info(f"Cotizacion {inquiry_id} rechazada, volviendo a awaiting_partners")
    return serialize_inquiry(updated)
