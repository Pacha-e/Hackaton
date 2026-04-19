# PQRSD Medellín — OmegaHack 2026 (Grupo NOVA / EAFIT)

Stack unificado: **Django 4.2** (PQRSD + IA Gemini), **API REST** (`/api/v1/`) y **Chatwoot** en Docker.

## Qué tienes que hacer tú (solo esto)

1. Abre **PowerShell** o **CMD**.
2. Ve a la carpeta del proyecto (ajusta la ruta si la tuya es distinta):

```powershell
cd C:\Users\EMMANUEL\hackathon
```

3. Crea el `.env` de Django si aún no existe: copia `.env.example` y renómbralo a `.env` (o `copy .env.example .env`).
4. Arranca **todo** (Django + Chatwoot). La primera vez puede tardar **varios minutos** porque Chatwoot ejecuta solo `rails db:chatwoot_prepare` antes de levantar la web.

```powershell
docker compose up --build -d
```

5. Migraciones y datos de prueba de Django:

```powershell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

6. Abre en el navegador:
   - Django: http://localhost:8090  
   - API: http://localhost:8090/api/v1/  
   - Chatwoot: http://localhost:3000  

**No hace falta** ejecutar comandos raros de Chatwoot a mano: el servicio `chatwoot_db_prepare` en `docker-compose.yml` prepara la base de datos antes de `chatwoot_rails` y `chatwoot_sidekiq`.

Si algo falla, mira los mensajes:

```powershell
docker compose logs chatwoot_db_prepare --tail 100
docker compose logs chatwoot_rails --tail 100
```

## Tabla de URLs

| Servicio | URL |
|----------|-----|
| Django (app web) | http://localhost:8090 |
| API (índice JSON) | http://localhost:8090/api/v1/ |
| Chatwoot | http://localhost:3000 |

La base de datos de Django expone el puerto **5434** en el PC. Chatwoot usa su propio Postgres dentro de Docker (`chatwoot_postgres`).

## Conectar Chatwoot con Django (webhook + agente Gemini)

Cada **mensaje entrante** del ciudadano en Chatwoot puede crear una **PQRSD** en Django y disparar la **misma clasificación con Gemini** que usarías en el panel (`/clasificacion/` o API `POST /api/v1/pqrsd/<id>/classify/`).

1. En `.env` de Django: `GEMINI_API_KEY` (Google AI Studio). Sin clave, el agente usa modo **simulado** (primera dependencia activa).
2. Opcional: `CHATWOOT_AUTO_CLASIFICAR=False` si solo quieres radicar sin llamar a Gemini.
3. Opcional: `CHATWOOT_WEBHOOK_SECRET=un_secreto` y en Chatwoot añade cabecera `X-Webhook-Token: un_secreto`.
4. En Chatwoot (como admin): **Ajustes → Integraciones → Webhooks** (o *Applications → Webhooks* según versión). Crea un webhook:
   - **URL:** `http://host.docker.internal:8090/api/v1/integrations/chatwoot/`
   - **Eventos:** al menos **`message_created`** (mensaje nuevo).
   - En **Linux**, sustituye `host.docker.internal` por la IP de tu máquina en la red Docker (p. ej. `172.17.0.1`).
5. Reinicia Django si cambiaste `.env`: `docker compose restart web`.

La respuesta JSON del webhook incluye `radicado`, `clasificacion` (sugerencia IA) y `agente: "gemini"` cuando todo va bien. Los IDs de Chatwoot se guardan en `omnicanal_meta` del PQRSD (evita duplicar el mismo mensaje).

Más contexto: `CLAUDE.md` en la raíz del repositorio.

## Publicar todo en una rama `main` (no existe en el remoto aún)

En el repo solo hay `feature/*`, `fix/*`, `woot`, etc. Para tener **`main`** con lo que llevas en `feature/ambiente-reparado`:

```powershell
cd C:\Users\EMMANUEL\hackathon
git checkout feature/ambiente-reparado
git pull
git checkout -b main
git push -u origin main
```

Luego en GitHub/GitLab puedes definir `main` como rama por defecto si lo deseas.

## Si Chatwoot sigue en error

1. Comprueba que terminó el prepare (sin error al final):

```powershell
docker compose logs chatwoot_db_prepare
```

2. Reinicia solo Chatwoot:

```powershell
docker compose restart chatwoot_rails chatwoot_sidekiq
```

3. Comando manual **solo si** el servicio automático falló (misma carpeta del proyecto):

```powershell
docker compose run --rm chatwoot_rails bundle exec rails db:chatwoot_prepare
docker compose up -d
```
