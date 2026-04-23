from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth import hash_password, require_admin
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Usuarios"])


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "admin"


class UserOut(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    active: bool
    created_at: datetime


def serialize_user(doc: dict) -> UserOut:
    return UserOut(
        id=str(doc["_id"]),
        username=doc["username"],
        full_name=doc.get("full_name", ""),
        role=doc["role"],
        active=doc.get("active", True),
        created_at=doc["created_at"],
    )


@router.get("/", response_model=list[UserOut], summary="Listar usuarios")
async def list_users(_: Annotated[dict, Depends(require_admin)]):
    db = get_db()
    users = []
    async for doc in db.users.find():
        users.append(serialize_user(doc))
    return users


@router.post("/", response_model=UserOut, status_code=201, summary="Crear usuario")
async def create_user(payload: UserCreate, _: Annotated[dict, Depends(require_admin)]):
    db = get_db()
    existing = await db.users.find_one({"username": payload.username})
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    doc = {
        "username": payload.username,
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name,
        "role": payload.role,
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(doc)
    created = await db.users.find_one({"_id": result.inserted_id})
    return serialize_user(created)


@router.patch("/{user_id}/toggle", response_model=UserOut, summary="Activar/desactivar usuario")
async def toggle_user(user_id: str, _: Annotated[dict, Depends(require_admin)]):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    new_state = not user.get("active", True)
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": new_state}})
    updated = await db.users.find_one({"_id": ObjectId(user_id)})
    return serialize_user(updated)
