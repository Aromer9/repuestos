from datetime import datetime, timezone
from typing import Annotated, Any
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
import re


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("ObjectId inválido")
        return str(v)


class InquiryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    rut: str = Field(..., description="RUT chileno (ej: 12.345.678-9)")
    phone: str = Field(..., description="Teléfono de contacto")
    brand: str = Field(..., description="Marca del vehículo")
    model: str = Field(..., description="Modelo del vehículo")
    year: int = Field(..., ge=1990, le=2030, description="Año del vehículo")
    vin: str | None = Field(None, description="Número VIN (opcional)")
    part_description: str = Field(..., min_length=5, description="Descripción del repuesto")
    product_id: str | None = Field(None, description="ID del producto del catálogo (opcional)")

    @field_validator("rut")
    @classmethod
    def validate_rut_format(cls, v: str) -> str:
        clean = re.sub(r"[.\-]", "", v).upper()
        if not re.match(r"^\d{7,8}[0-9K]$", clean):
            raise ValueError("Formato de RUT inválido")
        return v

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, v: str | None) -> str | None:
        if v and len(v) != 17:
            raise ValueError("El VIN debe tener exactamente 17 caracteres")
        return v.upper() if v else v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 8:
            raise ValueError("Teléfono inválido")
        return v


class InquiryInDB(InquiryCreate):
    id: str | None = Field(default=None, alias="_id")
    status: str = Field(default="pending", description="Estado: pending, quoted, closed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class InquiryResponse(BaseModel):
    id: str
    name: str
    rut: str
    phone: str
    brand: str
    model: str
    year: int
    vin: str | None = None
    part_description: str
    product_id: str | None = None
    status: str
    agent_status: str | None = None
    partners_contacted: int | None = None
    created_at: datetime
    updated_at: datetime
