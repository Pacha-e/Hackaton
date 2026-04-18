# CLAUDE.md — PQRSD Medellín (OmegaHack 2026)

Proyecto del **Grupo NOVA / EAFIT** para OmegaHack 2026.
Reto: Secretaría de Desarrollo Económico — gestión inteligente de PQRSD.

## Stack

Django 4.2 + PostgreSQL 15 + Docker Compose + Google Gemini 1.5 Flash (free tier).

## Comandos rápidos

```bash
# Levantar todo
docker compose up --build -d

# Migraciones
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Cargar datos de prueba (idempotente)
docker compose exec web python manage.py seed_data

# Tests
docker compose exec web python manage.py test

# App en http://localhost:8000
```

## Estructura de apps

- **`apps.conocimiento`** — Componente A: Base de conocimiento con 26 dependencias de la Alcaldía y banco de precedentes de respuesta.
- **`apps.pqrsd`** — Modelo PQRSD central: tipos, estados, canales, SLA (calculado al vuelo sin Celery). `PQRSD.dias_restantes()` y `en_alerta()` son propiedades calculadas.
- **`apps.clasificacion`** — Componente B: Gemini 1.5 Flash clasifica automáticamente → funcionario **debe** validar. Ver `gemini_service.py`. Si no hay API key, usa `_clasificacion_simulada()` como fallback.
- **`apps.sintesis`** — Componente C: Síntesis en 3 capas (resumen ejecutivo / datos estructurados / análisis jurídico). Ver `gemini_sintesis.py`.
- **`apps.funcionarios`** — Dashboard para enlace PQRSD y asesor jurídico. Filtros, alertas SLA, cambio de estado.

## Decisiones de diseño clave

- **Sin Celery/Redis**: SLA se calcula en vista/template con `fecha_limite - date.today()`. No se necesitan workers.
- **Sin n8n**: Canal de entrada es `CharField` con choices. Simula WhatsApp, email, etc. via seed data.
- **IA no toma decisiones**: Toda sugerencia de Gemini requiere validación humana explícita (cumple Ley 1755/2015).
- **Fecha límite**: calculada en días hábiles al crear la PQRSD (función `_calcular_fecha_limite` en `models.py`).
- **API key Gemini**: Obtener gratis en https://ai.google.dev con cuenta institucional EAFIT (@eafit.edu.co).

## Usuarios demo

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin1234` | Superusuario |
| `enlace1` | `pqrsd2026` | Enlace PQRSD |
| `juridico1` | `pqrsd2026` | Asesor Jurídico |

## Marco legal

- Ley 1755/2015 — Derecho de Petición (15 días hábiles)
- Ley 1437/2011 — CPACA
- Ley 1581/2012 — Protección de datos personales
- Decreto Municipal 883/2015 — PQRSD Alcaldía Medellín

## Rubrica OmegaHack (referencia)

5 pilares × 20% = Arquitectura+IA | Impacto/Negocio | UX | Innovación+Docs | Pitch.
Bonus hasta 10% por mini-retos. Documentar 5 hitos en bitácora (Innovation pillar).
