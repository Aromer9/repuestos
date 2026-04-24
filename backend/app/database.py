import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "argparts"

    # Evolution API (WhatsApp open source)
    evolution_api_url: str = ""       # ej: https://evolution.tudominio.railway.app
    evolution_api_key: str = ""       # API key global de la instancia
    evolution_instance: str = ""      # nombre de la instancia, ej: argparts

    # AI providers (opcionales)
    anthropic_api_key: str = ""
    open_ai_api_key: str = ""
    openai_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

client: AsyncIOMotorClient | None = None


async def connect_db():
    global client
    uri = settings.mongodb_uri.strip().strip('"').strip("'")
    try:
        client = AsyncIOMotorClient(
            uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=8000,
        )
        await client.admin.command("ping")
        print(f"✅ Conectado a MongoDB: {settings.database_name}")
    except Exception as e:
        print(f"⚠️  MongoDB no disponible: {e}")
        print("⚠️  El servidor arrancará de todas formas — verifica MONGODB_URI y Network Access en Atlas")


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 Conexión MongoDB cerrada")


def get_db():
    return client[settings.database_name]
