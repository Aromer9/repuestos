from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth import require_admin
from app.database import get_db

router = APIRouter(prefix="/partners", tags=["Partners"])


class PartnerCreate(BaseModel):
    name: str
    brand: str
    address: str
    phone: str
    notes: str | None = None
    active: bool = True


class PartnerOut(BaseModel):
    id: str
    name: str
    brand: str
    address: str
    phone: str
    notes: str | None
    active: bool
    created_at: datetime


def serialize(doc: dict) -> PartnerOut:
    return PartnerOut(
        id=str(doc["_id"]),
        name=doc["name"],
        brand=doc["brand"],
        address=doc["address"],
        phone=doc["phone"],
        notes=doc.get("notes"),
        active=doc.get("active", True),
        created_at=doc["created_at"],
    )


@router.get("/", response_model=list[PartnerOut], summary="Listar partners")
async def list_partners(_: Annotated[dict, Depends(require_admin)]):
    db = get_db()
    partners = []
    async for doc in db.partners.find().sort("name", 1):
        partners.append(serialize(doc))
    return partners


@router.post("/", response_model=PartnerOut, status_code=201, summary="Crear partner")
async def create_partner(payload: PartnerCreate, _: Annotated[dict, Depends(require_admin)]):
    db = get_db()
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db.partners.insert_one(doc)
    created = await db.partners.find_one({"_id": result.inserted_id})
    return serialize(created)


@router.put("/{partner_id}", response_model=PartnerOut, summary="Actualizar partner")
async def update_partner(
    partner_id: str,
    payload: PartnerCreate,
    _: Annotated[dict, Depends(require_admin)],
):
    if not ObjectId.is_valid(partner_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    db = get_db()
    result = await db.partners.find_one_and_update(
        {"_id": ObjectId(partner_id)},
        {"$set": payload.model_dump()},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
    return serialize(result)


@router.delete("/{partner_id}", status_code=204, summary="Eliminar partner")
async def delete_partner(partner_id: str, _: Annotated[dict, Depends(require_admin)]):
    if not ObjectId.is_valid(partner_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    db = get_db()
    result = await db.partners.delete_one({"_id": ObjectId(partner_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
