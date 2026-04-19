# PQRSD Medellín — OmegaHack 2026 (Grupo NOVA / EAFIT)

Sistema inteligente de gestión de PQRSD para la Secretaría de Desarrollo Económico de Medellín.  
Pipeline de 9 agentes Claude (Haiku · Sonnet · Opus) que procesa peticiones ciudadanas end-to-end.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Django 4.2 + Django REST Framework 3.15 |
| Base de datos | PostgreSQL 15 |
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS 4 |
| IA | Anthropic Claude (Haiku / Sonnet / Opus) |
| Infra | Docker Compose |

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose)
- [Make](https://gnuwin32.sourceforge.net/packages/make.htm) (Windows: instalar via `winget install GnuWin32.Make`)
- Clave de API de Anthropic → [console.anthropic.com](https://console.anthropic.com)

## Setup en un comando

```bash
cp .env.example .env      # copia la configuración base
# edita .env y pon tu ANTHROPIC_API_KEY
make setup                # build + migraciones + datos demo
```

Eso es todo. En 2–3 minutos el sistema estará levantado.

## URLs

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Portal ciudadano | http://localhost:5175/pqrsd/ | Radicar y consultar PQRSD |
| Dashboard staff | http://localhost:5175/funcionarios/ | Gestión y clasificación |
| API REST | http://localhost:5175/api/v1/ | Todos los endpoints |
| SPA React | http://localhost:5175/ | Interfaz staff moderna |

## Usuarios demo

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin1234` | Superusuario |
| `enlace1` | `pqrsd2026` | Enlace PQRSD |
| `juridico1` | `pqrsd2026` | Asesor Jurídico |

## Comandos Make

```bash
make help        # ver todos los comandos disponibles

# Ciclo de vida
make run         # levantar servicios
make stop        # detener servicios
make restart     # reiniciar servicios
make logs        # ver logs en tiempo real
make build       # reconstruir imágenes

# Desarrollo
make shell       # Django shell (manage.py shell)
make bash        # bash dentro del contenedor web
make test        # correr tests

# Base de datos
make migrate     # makemigrations + migrate
make seed        # cargar datos demo (idempotente)
make reset       # flush + migrate + seed
make clean       # eliminar contenedores y volúmenes
```

## Pipeline de agentes IA

Cada PQRSD que entra pasa por 9 agentes en secuencia:

```
M1 IntakeAgent   (Haiku)  → Normalización multi-canal
M3 FilterAgent   (Haiku)  → Admisibilidad (lenguaje, duplicados, claridad)
M8 SLAAgent      (Haiku)  → Cálculo de plazos en días hábiles (Ley 1755/2015)
M4 SplitterAgent (Sonnet) → División de PQRSDs compuestas multi-secretaría
M2 RouterAgent   (Sonnet) → Enrutamiento a 26 secretarías (Decreto 883/2015)
M9 PrivacyAgent  (Sonnet) → Habeas Data y anonimización (Ley 1581/2012)
M6 KnowledgeAgent(Sonnet) → Banco de precedentes con scoring semántico
M5 ResponseAgent (Opus)   → Respuesta humanizada anti-alucinación
M7 DeliveryAgent (Haiku)  → Entrega multi-canal con confirmación
```

### Endpoints del pipeline

```http
POST /api/v1/pqrsd/submit-pipeline/    # Radicar + procesar en un paso (ciudadano)
POST /api/v1/pqrsd/<pk>/pipeline/      # Re-procesar una PQRSD existente (staff)
```

Requiere `ANTHROPIC_API_KEY` en `.env`. Si no está configurada, los endpoints devuelven `503`.

## Estructura del proyecto

```
apps/
  agentes/          ← 9 agentes Claude + orquestador
  api/              ← REST API (16 endpoints)
  clasificacion/    ← Clasificación IA con validación humana
  conocimiento/     ← 26 dependencias + banco de precedentes
  funcionarios/     ← Dashboard Django templates
  pqrsd/            ← Modelo central PQRSD
  sintesis/         ← Síntesis en 3 capas
frontend/           ← SPA React
config/             ← Settings Django
Makefile            ← Comandos de desarrollo
docker-compose.yml  ← 3 servicios: db, web, frontend
```

## Marco legal

- **Ley 1755/2015** — Derecho de Petición (plazos en días hábiles)
- **Ley 1437/2011** — CPACA
- **Ley 1581/2012** — Protección de datos personales (Habeas Data)
- **Decreto Municipal 883/2015** — Competencias por secretaría, Alcaldía de Medellín

## Variables de entorno

Ver `.env.example` para la lista completa. Las esenciales:

| Variable | Descripción |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Clave API para los agentes Claude |
| `SECRET_KEY` | Clave secreta Django (generar con `python -c "import secrets; print(secrets.token_hex(50))"`) |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `DB_*` | Configuración PostgreSQL |
