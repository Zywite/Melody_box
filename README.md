# MelodyBox

Un reproductor de música y video para red local, construido con FastAPI.

## Características

- **Autenticación segura** — JWT con registro y login
- **Audio y Video** — Sube y reproduce MP3, WAV, FLAC, OGG, M4A, MP4, MKV, AVI, WebM, MOV
- **Streaming** — Reproducción por partes con soporte byte-range
- **Búsqueda** — Por título, artista o álbum
- **Playlists** — Crea y gestiona listas de reproducción
- **Favoritos** — Marca canciones como favoritas
- **Multi-usuario** — Cada usuario tiene sus playlists y favoritos
- **Acceso en red** — Cualquier dispositivo en la misma red puede acceder
- **Interfaz moderna** — Diseño dark theme con glassmorphism

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | FastAPI, SQLAlchemy, JWT, bcrypt |
| Frontend | Vue 3 + Vite + Tailwind CSS |
| Base de datos | PostgreSQL (recomendado) / SQLite |
| Servidor | Uvicorn (ASGI) |

## Instalación

### Requisitos

- Python 3.12+
- PostgreSQL (recomendado) o SQLite

### Pasos

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# 3. Instalar dependencias del backend
pip install -r requirements.txt

# 4. Copiar y configurar .env
copy .env.example src/.env
# Editar src/.env con tu configuración

# 5. Instalar dependencias del frontend
cd frontend
npm install
```

> **Nota:** El frontend se sirve desde el backend en producción. Para desarrollo, puedes ejecutar `npm run dev` en la carpeta `frontend` y conectar al backend en `http://localhost:8001`.

## Inicio rápido

### Opción 1: Script (recomendado)

```bash
python scripts/start_server.py
```

### Opción 2: Batch (Windows)

```bash
scripts\run_server.bat
```

### Opción 3: Manual

```bash
cd src
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

El servidor arranca en **http://localhost:8001**

| Servicio | URL |
|---|---|
| Frontend | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |
| Health | http://localhost:8001/health |

## Acceso desde otros dispositivos

1. Conecta tu laptop y el otro dispositivo a la **misma red WiFi**
2. Averigua tu IP local: `ipconfig` (busca IPv4, ej: `192.168.1.8`)
3. Desde el otro dispositivo abre: `http://TU_IP:8001`

> **Nota:** Algunas redes con aislamiento de clientes (universidades, hoteles) pueden bloquear la comunicación entre dispositivos. En ese caso, usa un hotspot personal.

## Estructura del proyecto

```
MelodyBox/
├── src/                     # Backend
│   ├── app/
│   │   ├── core/            # Config, BD, seguridad
│   │   ├── models/          # Modelos SQLAlchemy
│   │   ├── routes/          # Endpoints API
│   │   ├── services/        # Lógica de negocio
│   │   ├── schemas.py       # Schemas Pydantic
│   │   └── main.py          # App principal
│   └── .env                 # Configuración (no incluir en git)
├── frontend/                # Frontend Vue 3 + Vite + Tailwind
│   ├── src/
│   │   ├── assets/          # Estilos, imágenes
│   │   ├── components/      # Componentes Vue
│   │   ├── composables/     # Composables Vue
│   │   ├── stores/          # Pinia stores
│   │   ├── views/           # Vistas
│   │   └── router/          # Vue Router
│   ├── package.json
│   └── vite.config.js
├── docs/                    # Documentación
│   ├── MANUAL_USUARIO.md
│   ├── API_REFERENCE.md
│   ├── ARQUITECTURA.md
│   ├── POSTGRESQL_SETUP.md
│   ├── STREAMING_GUIDE.md
│   └── SRS.pdf              # Especificación de requisitos
├── scripts/                 # Scripts de utilidad
├── music_storage/           # Archivos subidos
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
```

## Documentación adicional

| Archivo | Contenido |
|---|---|
| [`docs/MANUAL_USUARIO.md`](docs/MANUAL_USUARIO.md) | Guía paso a paso de la interfaz |
| [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | Referencia completa de la API |
| [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) | Arquitectura, patrones de diseño, BD |
| [`docs/POSTGRESQL_SETUP.md`](docs/POSTGRESQL_SETUP.md) | Instalación de PostgreSQL |
| [`docs/STREAMING_GUIDE.md`](docs/STREAMING_GUIDE.md) | Cómo funciona el streaming |

## Solución de problemas

| Problema | Solución |
|---|---|
| Puerto 8001 bloqueado | Cambia el puerto en `scripts/start_server.py` |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `UniqueViolation` en upload | Reinicia el servidor (rutas absolutas) |
| No conecta desde otro dispositivo | Verifica firewall y que estén en la misma red |
| Archivos no se reproducen | Verifica que el archivo existe en `music_storage/` |

## Formatos soportados

**Audio:** MP3, WAV, FLAC, OGG, M4A  
**Video:** MP4, MKV, AVI, WebM, MOV