# JDMParts — Backend API

FastAPI + MongoDB Atlas para captura de cotizaciones.

## Configuración rápida

### 1. Crear cuenta en MongoDB Atlas (gratis)

1. Ve a [https://cloud.mongodb.com](https://cloud.mongodb.com) y crea una cuenta gratuita.
2. Crea un nuevo proyecto → **Create a Cluster** → elige **M0 Free**.
3. En **Database Access**: crea un usuario con contraseña.
4. En **Network Access**: agrega `0.0.0.0/0` para permitir acceso desde cualquier IP (en desarrollo).
5. En tu cluster → **Connect** → **Drivers** → elige **Python** → copia la URI de conexión.

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y pega tu URI de Atlas:

```
MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=jdmparts
```

### 3. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Correr el servidor

```bash
uvicorn main:app --reload --port 8000
```

El servidor estará en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/inquiries/` | Crear cotización |
| `GET` | `/api/inquiries/` | Listar cotizaciones |
| `GET` | `/api/inquiries/{id}` | Obtener cotización por ID |
| `PATCH` | `/api/inquiries/{id}/status` | Cambiar estado |

## Estados de una cotización

- `pending` — recién recibida, sin procesar
- `quoted` — el agente ya cotizó con proveedores
- `closed` — cerrada (convertida o descartada)

## Ejemplo de payload (POST /api/inquiries/)

```json
{
  "name": "Juan Pérez",
  "rut": "12.345.678-9",
  "phone": "+56912345678",
  "brand": "Subaru",
  "model": "Impreza",
  "year": 2018,
  "vin": "JF1GP7EC2EG999999",
  "part_description": "Bomba de agua original",
  "product_id": null
}
```
