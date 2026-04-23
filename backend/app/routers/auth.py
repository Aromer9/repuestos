from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth import (
    create_access_token,
    get_current_user,
    verify_password,
)
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserOut(BaseModel):
    username: str
    full_name: str
    role: str


@router.post("/login", response_model=Token, summary="Iniciar sesión")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    db = get_db()
    user = await db.users.find_one({"username": form.username, "active": True})

    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user["username"], "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "full_name": user.get("full_name", ""),
            "role": user["role"],
        },
    }


@router.get("/me", summary="Usuario actual")
async def me(current_user: Annotated[dict, Depends(get_current_user)]):
    return {
        "username": current_user["username"],
        "full_name": current_user.get("full_name", ""),
        "role": current_user["role"],
    }
