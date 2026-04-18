# TODO HANDOFF — PQRSD Medellín (OmegaHack 2026)

## Project context
Django 4.2 + PostgreSQL 15 + Docker Compose + Google Gemini 1.5 Flash (fallback simulation if no key).
Two audiences: **citizens** (public portal) and **functionaries** (internal dashboard).
Branch: `feature/mvp-inicial` on https://github.com/thomaszambrano/Hackaton.git — already pushed (65 files).

## Run the project
```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
# → http://localhost:8000
```

Demo credentials: `admin/admin1234`, `enlace1/pqrsd2026`, `juridico1/pqrsd2026`

---

## PENDING TASKS (ordered by priority)

### 1. Visual split — citizen portal vs. functionary dashboard [P1 — CRITICAL]
**Problem**: Both surfaces share identical base.html, same bg-light body, same dark navbar. Zero visual differentiation.
**Fix**:
- Add a `{% block body_class %}{% endblock %}` to `<body>` in `templates/base.html`
- In functionary templates set `{% block body_class %}dashboard{% endblock %}`
- In `base.html <style>`: add `body.dashboard { background: #0f1e17; color: #e8f0eb; }` and override card/table colors for dark theme
- Citizen portal stays light — no changes needed to citizen templates

### 2. Apply brand colors — Medellín green #00a859 [P2]
**Problem**: `--medellin-green: #00a859` is declared but Bootstrap's `btn-success` (#198754) and `btn-primary` (#0d6efd) are used everywhere instead. Brand not applied.
**Fix** in `base.html <style>`:
```css
:root {
  --bs-success: #00a859;
  --bs-success-rgb: 0, 168, 89;
  --bs-btn-bg: #00a859; /* for .btn-success */
}
/* Remove all btn-primary usage in citizen templates — replace with btn-success */
```
Files to update: `templates/pqrsd/home.html` (Consultar button: change `btn-primary` → `btn-outline-success`)

### 3. Make stat cards functional on dashboard [P3]
**Problem**: 6 metric cards (Total, Radicadas, En trámite, etc.) are not clickable — they show counts but don't filter the table.
**Fix** in `templates/funcionarios/dashboard.html`: wrap each card in an anchor tag:
```html
<a href="?estado=vencida" class="text-decoration-none">
  <div class="card ...">...</div>
</a>
```
Mapping: Total→no filter, Radicadas→`?estado=radicada`, En trámite→`?estado=en_tramite`, Respondidas→`?estado=respondida`, Alertas→`?alertas=1`, Vencidas→`?estado=vencida`

### 4. Fix tipo cards on citizen homepage [P4]
**Problem**: 6 tipo cards (Petición, Queja, Reclamo, etc.) look interactive but lead nowhere. False affordance.
**Fix option A (simpler)**: Convert each card to a link that pre-selects the type on the radicar form:
```html
<a href="{% url 'radicar_pqrsd' %}?tipo={{ tipo }}" class="card ...">
```
Then in `apps/pqrsd/views.py` `radicar_pqrsd()`, pre-populate form: `form = PQRSDCiudadanoForm(initial={'tipo': request.GET.get('tipo', '')})`
**Fix option B**: Remove the 6 cards entirely — the form already has a tipo dropdown.

### 5. Add empty states [P5]
**Files to update**:
- `templates/funcionarios/dashboard.html`: the `{% empty %}` row currently just says "No hay solicitudes..." — add an icon and a helpful message
- `templates/pqrsd/consultar.html`: when radicado not found, show a visual not-found state (not just a Django message)

### 6. Fix stale "Gemini" label in revisar.html [cosmetic]
**File**: `templates/clasificacion/revisar.html` line ~43
Change: `Sugerencia de Gemini 1.5 Flash` → `Sugerencia del asistente IA`
Also change the `<h6>` model label to use `{{ clasificacion.modelo_usado }}` already available in context.

### 7. Chatwoot integration (user requested, not started)
User mentioned replacing or supplementing Gemini with Chatwoot. Chatwoot is an open-source omnichannel customer support platform.
**Likely intent**: use Chatwoot as an additional PQRSD intake channel (WhatsApp, email conversations → auto-create PQRSD).
**Not implemented yet** — needs clarification on whether this is:
  a) Chatwoot webhook → Django `radicar_pqrsd` (creates PQRSD from Chatwoot conversation)
  b) Embedding Chatwoot live chat widget on the citizen portal

### 8. Move hackathon credit out of citizen footer [cosmetic]
**File**: `templates/base.html` line ~150
Remove `OmegaHack 2026 — Grupo NOVA / EAFIT` from the public-facing footer.
Move to an HTML comment or only show when `user.is_staff`.

---

## Already completed / working
- All 5 Django apps with models, views, URLs, forms
- 26 Medellín dependencies seeded (SDEC, SDIS, SSPM, SOMA, etc.)
- 10 realistic PQRSD seeded across communes
- Gemini classification + fallback simulation
- 3-layer synthesis (resumen ejecutivo / datos estructurados / análisis jurídico)
- SLA tracking via `dias_restantes()`, `en_alerta()`, `vencida()` model properties
- Human-in-the-loop validation enforced (ClasificacionIA.aceptada)
- Functionary dashboard with filters and SLA table
- `revisar.html` dropdown pre-selection bug — FIXED ({% if %} moved outside attribute)

## Key files
- `apps/clasificacion/gemini_service.py` — AI classification, fallback at bottom
- `apps/sintesis/gemini_sintesis.py` — 3-layer synthesis, fallback at bottom
- `apps/pqrsd/models.py` — PQRSD model, SLA logic, `_calcular_fecha_limite()`
- `apps/pqrsd/management/commands/seed_data.py` — seed command, fully idempotent
- `templates/base.html` — global shell, CSS variables, SLA card classes
- `templates/funcionarios/dashboard.html` — functionary main view
- `templates/clasificacion/revisar.html` — AI review + human validation
- `.impeccable.md` — design context (formal/institutional citizen, dark ops dashboard)
