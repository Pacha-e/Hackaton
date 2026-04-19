#!/bin/bash
# Arrancar la app en producción — ejecutar después de configurar .env
set -e
cd /home/ubuntu/hackathon

echo "=== Levantando servicios ==="
docker compose -f docker-compose.prod.yml up -d --build

echo "=== Esperando que la DB esté lista ==="
sleep 10

echo "=== Migraciones ==="
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput

echo "=== Static files ==="
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "=== Datos de prueba ==="
docker compose -f docker-compose.prod.yml exec web python manage.py seed_data

echo ""
echo "=== LISTO ==="
echo "API disponible en: http://$(curl -s ifconfig.me):8090"
