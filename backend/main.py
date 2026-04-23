import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_db, close_db
from app.routers import inquiries, auth, users, partners, webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="ARGParts API",
    description="API para captura y gestión de cotizaciones de repuestos japoneses.",
    version="1.0.0",
    lifespan=lifespan,
)

# Orígenes permitidos: locales + Railway (via variable de entorno FRONTEND_URL)
_extra_origin = os.getenv("FRONTEND_URL", "")
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]
if _extra_origin:
    ALLOWED_ORIGINS.append(_extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(inquiries.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(partners.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "ARGParts API"}


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok"}
