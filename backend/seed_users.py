"""
Ejecutar una vez para crear los usuarios admin iniciales:
  python seed_users.py
"""
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMINS = [
    {"username": "aldo", "password": "jdm2026!", "full_name": "Aldo Romero", "role": "admin"},
    {"username": "socio", "password": "jdm2026!", "full_name": "Mi Socio", "role": "admin"},
]


async def seed():
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "jdmparts")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    db = client[db_name]

    for admin in ADMINS:
        existing = await db.users.find_one({"username": admin["username"]})
        if existing:
            print(f"⚠️  Usuario '{admin['username']}' ya existe, omitiendo.")
            continue
        doc = {
            "username": admin["username"],
            "password_hash": pwd_context.hash(admin["password"]),
            "full_name": admin["full_name"],
            "role": admin["role"],
            "active": True,
            "created_at": datetime.now(timezone.utc),
        }
        await db.users.insert_one(doc)
        print(f"✅ Usuario creado: {admin['username']} / {admin['password']}")

    await db.users.create_index("username", unique=True)
    print("\n🚀 Índice único en 'username' creado.")
    client.close()


asyncio.run(seed())
