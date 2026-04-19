.PHONY: help setup run stop restart build logs shell test seed migrate reset clean

help:
	@echo ""
	@echo "PQRSD Medellín — Comandos disponibles"
	@echo "======================================"
	@echo "  make setup     → Primera vez: construir, migrar y cargar datos demo"
	@echo "  make run       → Levantar todos los servicios"
	@echo "  make stop      → Detener todos los servicios"
	@echo "  make restart   → Reiniciar todos los servicios"
	@echo "  make build     → Reconstruir imágenes Docker"
	@echo "  make logs      → Ver logs en tiempo real"
	@echo "  make shell     → Shell Django (manage.py shell)"
	@echo "  make bash      → Bash dentro del contenedor web"
	@echo "  make test      → Correr tests"
	@echo "  make seed      → Cargar datos demo (idempotente)"
	@echo "  make migrate   → Crear y aplicar migraciones"
	@echo "  make reset     → Borrar DB y volver a cargar datos demo"
	@echo "  make clean     → Eliminar contenedores y volúmenes"
	@echo ""
	@echo "URLs:"
	@echo "  Portal ciudadano → http://localhost:8090/pqrsd/"
	@echo "  Dashboard staff  → http://localhost:8090/funcionarios/"
	@echo "  API REST         → http://localhost:8090/api/v1/"
	@echo "  SPA React        → http://localhost:5175/"
	@echo ""

# ── Setup inicial ────────────────────────────────────────────────────────────

setup:
	@echo "→ Verificando .env..."
	@test -f .env || (cp .env.example .env && echo "  ✓ .env creado desde .env.example — edita ANTHROPIC_API_KEY antes de continuar")
	@echo "→ Construyendo imágenes..."
	docker compose up --build -d
	@echo "→ Esperando base de datos..."
	@sleep 5
	@echo "→ Aplicando migraciones..."
	docker compose exec web python manage.py migrate
	@echo "→ Cargando datos demo..."
	docker compose exec web python manage.py seed_data
	@echo ""
	@echo "✓ Listo. Accede en:"
	@echo "  Portal ciudadano → http://localhost:8090/pqrsd/"
	@echo "  Dashboard staff  → http://localhost:8090/funcionarios/"
	@echo "  SPA React        → http://localhost:5175/"
	@echo "  Usuario: admin / Contraseña: admin1234"

# ── Ciclo de vida ────────────────────────────────────────────────────────────

run:
	docker compose up -d

stop:
	docker compose stop

restart:
	docker compose restart

build:
	docker compose up --build -d

logs:
	docker compose logs -f

# ── Desarrollo ───────────────────────────────────────────────────────────────

shell:
	docker compose exec web python manage.py shell

bash:
	docker compose exec web bash

test:
	docker compose exec web python manage.py test

# ── Base de datos ────────────────────────────────────────────────────────────

migrate:
	docker compose exec web python manage.py makemigrations
	docker compose exec web python manage.py migrate

seed:
	docker compose exec web python manage.py seed_data

reset:
	@echo "→ Borrando datos y recargando..."
	docker compose exec web python manage.py flush --no-input
	docker compose exec web python manage.py migrate
	docker compose exec web python manage.py seed_data
	@echo "✓ Base de datos restaurada"

# ── Limpieza ─────────────────────────────────────────────────────────────────

clean:
	@echo "⚠ Esto elimina contenedores y volúmenes (incluyendo la DB)"
	@read -p "¿Continuar? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	@echo "✓ Limpieza completa"
