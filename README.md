# MelodyBox

Un reproductor de música y video para red local, construido con FastAPI y Vue 3.

## Características

- **Autenticación segura** — JWT con registro y login
- **Audio y Video** — Sube y reproduce MP3, WAV, FLAC, OGG, M4A, MP4, MKV, AVI, WebM, MOV
- **Streaming** — Reproducción por partes con soporte byte-range
- **YouTube** — Busca, filtra y descarga música desde YouTube
- **Análisis FFT** — Espectro de frecuencias y espectrograma de tus canciones
- **Playlists** — Crea y gestiona listas de reproducción
- **Favoritos** — Marca canciones como favoritas
- **Modo oscuro** — Alterna entre tema claro y oscuro
- **Multi-usuario** — Cada usuario tiene sus playlists y favoritos
- **Acceso en red** — Cualquier dispositivo en la misma red puede acceder
- **FAQ** — Sección de preguntas frecuentes integrada

## Tecnologías

| Capa | Tecnología |
|---|---|---|
| Backend | FastAPI, SQLAlchemy, JWT, bcrypt, librosa, ARQ |
| Frontend | Vue 3 + Vite + Tailwind CSS + Pinia |
| Base de datos | PostgreSQL (+ SQLite fallback) |
| Cache / Colas | Redis |
| Worker async | ARQ (FFT, YouTube downloads) |
| Proxy inverso | Nginx (static files, API proxy) |
| Contenedores | Docker + Docker Compose |

## Instalación

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Pasos (recomendado — con Docker)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Zywite/Melody_box.git
cd Melody_box

# 2. Buildear e iniciar
docker compose up --build

# 3. Abrir en el navegador
http://localhost:8001
```

La primera vez puede tardar unos minutos (build del frontend + instalación de dependencias Python).

> Docker Compose inicia 4 servicios: **backend** (FastAPI + Uvicorn), **nginx** (proxy inverso), **redis** (cache/colas), **worker** (ARQ para FFT y descargas).

### Sin Docker (desarrollo local)

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# 3. Instalar dependencias del backend
pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env
# Editar .env con tu configuración de PostgreSQL

# 5. Instalar dependencias del frontend
cd frontend
npm install
npm run build
cd ..

# 6. Iniciar servidor
python scripts/start_server.py
```

## Inicio rápido

### Opción 1: Docker (recomendado)

```bash
docker compose up
```

Para reconstruir después de cambios:
```bash
docker compose up --build
```

### Opción 2: Script

```bash
python scripts/start_server.py
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
│   │   ├── core/            # Config, BD, seguridad, Redis helper
│   │   ├── models/          # Modelos SQLAlchemy (incl. Task)
│   │   ├── routes/          # Endpoints API (incl. tasks, youtube)
│   │   ├── services/        # Lógica de negocio (FFT, users, songs, playlists)
│   │   ├── schemas.py       # Schemas Pydantic
│   │   └── main.py          # App principal
│   └── worker.py            # Worker ARQ (FFT + YouTube downloads)
├── frontend/                # Frontend Vue 3 + Vite + Tailwind
│   ├── src/
│   │   ├── assets/          # Estilos globales
│   │   ├── components/      # Componentes Vue (common, layout, player, effects)
│   │   ├── composables/     # useApi.js, useToast.js
│   │   ├── stores/          # Pinia stores (auth, library, player)
│   │   ├── views/           # 9 vistas (Home, Library, FFT, Upload, etc.)
│   │   └── router/          # Vue Router
│   ├── dist/                # Frontend compilado
│   └── package.json
├── data/
│   └── music/               # Archivos de audio/video subidos
├── src/tests/               # Tests (unitarios, integración, e2e)
├── docs/                    # Documentación
├── scripts/                 # Scripts de utilidad (presentar, run_worker)
├── nginx.conf               # Configuración Nginx
├── Dockerfile               # Imagen Docker multi-stage
├── docker-compose.yml       # Orquestación (4 servicios)
├── .env.example
├── requirements.txt
└── README.md
```

## Tests

El proyecto incluye **133 tests** en 3 categorías:

| Tipo | Carpeta | Tests | Qué cubren |
|------|---------|-------|------------|
| **Unitarios** | `src/tests/test_*service*`, `test_security*` | 55 | Hashing, JWT, CRUD de servicios sin IO |
| **Integración** | `src/tests/test_*api*`, `test_youtube*`, `test_rate_limiting*` | 71 | API vía TestClient (SQLite en memoria, Redis mockeado) |
| **E2E** | `src/tests/e2e/` | 7 | Archivos `.wav` reales, upload → stream → delete, full user journey |

Cobertura: **48/49 reglas de negocio (~98%)**.

### Ejecutar tests

```bash
# Todos los tests
pytest src/tests/ -q

# Solo unitarios
pytest src/tests/ -q -k "not api and not e2e and not rate"

# Solo integración
pytest src/tests/ -q -k "api and not e2e and not rate" --ignore=src/tests/e2e

# Solo e2e
pytest src/tests/e2e/ -q

# Rate limiting (requiere Redis, se salta en CI)
pytest src/tests/test_rate_limiting.py -q

# Con Docker
docker compose run --build test
```

> Los tests se ejecutan automáticamente antes de cada `git push` vía pre-push hook.

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
| `ModuleNotFoundError: No module named 'app'` | Rebuild con `docker compose up --build` |
| `No module named 'email_validator'` | Rebuild con `docker compose up --build` |
| Frontend muestra JSON en vez de HTML | Rebuild con `docker compose up --build` |
| Puerto 8001 bloqueado | Cambia el puerto en `docker-compose.yml` |
| No conecta desde otro dispositivo | Verifica firewall y que estén en la misma red |

## Formatos soportados

**Audio:** MP3, WAV, FLAC, OGG, M4A
**Video:** MP4, MKV, AVI, WebM, MOV
**YouTube download:** M4A, MP3, WAV, FLAC, OGG (audio) / MP4, MKV, WebM (video)
