# PQRSD Medellín — OmegaHack 2026 (Grupo NOVA / EAFIT)

Stack unificado: **Django 4.2** (PQRSD + IA Gemini), **API REST** (`/api/v1/`) y **Chatwoot** (omnicanalidad opcional en Docker).

## Arranque rápido

1. Variables de entorno: copia `.env.example` → `.env` para Django. Chatwoot lee `.env.chatwoot` (hay un archivo de demo en el repo; en producción rota `SECRET_KEY_BASE`).
2. Levanta servicios:

```bash
docker compose up --build -d
```

3. Migraciones y datos demo:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

## URLs locales

| Servicio | URL |
|----------|-----|
| Django (app web) | http://localhost:8090 |
| API REST navegable | http://localhost:8090/api/v1/ |
| Chatwoot | http://localhost:3000 |

La base de datos de Django está en el puerto **5434** (mapeo host). Chatwoot usa Postgres **pgvector** solo dentro de la red Docker (`chatwoot_postgres`).

## Conectar Chatwoot con Django

1. Crea la cuenta inicial en Chatwoot (`http://localhost:3000`) si `ENABLE_ACCOUNT_SIGNUP=true`.
2. Configura un **webhook** (Automation o integración HTTP) hacia:

   `http://host.docker.internal:8090/api/v1/integrations/chatwoot/`

   (En Linux puede ser la IP del host en lugar de `host.docker.internal`.)

3. Opcional: define `CHATWOOT_WEBHOOK_SECRET` en `.env` y envía la misma cadena en la cabecera `X-Webhook-Token` desde Chatwoot.

El endpoint acepta:

- JSON directo con `asunto` y `descripcion` (y opcionalmente `canal_entrada`, `nombre_ciudadano`, etc.) para crear una PQRSD.
- Eventos tipo `message_created` de Chatwoot (intenta mapear `message.content` a una nueva PQRSD).

Más detalle operativo: ver `CLAUDE.md` en la raíz del repositorio.
