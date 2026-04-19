#!/bin/bash
# Setup EC2 Ubuntu 22.04 para PQRSD — ejecutar como ubuntu
set -e

echo "=== Instalando Docker ==="
sudo apt-get update -q
sudo apt-get install -y docker.io docker-compose-plugin git curl
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

echo "=== Clonando repositorio ==="
git clone https://github.com/thomaszambrano/Hackaton.git /home/ubuntu/hackathon
cd /home/ubuntu/hackathon

echo "=== Creando .env de producción ==="
cat > .env << 'ENVEOF'
SECRET_KEY=CAMBIAR_POR_CLAVE_SEGURA_ALEATORIA
DEBUG=False
ALLOWED_HOSTS=CAMBIAR_POR_IP_EC2,localhost
DB_NAME=pqrsddb
DB_USER=postgres
DB_PASSWORD=CAMBIAR_POR_PASSWORD_SEGURO
DB_HOST=db
DB_PORT=5432
ANTHROPIC_API_KEY=CAMBIAR_POR_TU_KEY
CORS_ALLOWED_ORIGINS=https://CAMBIAR_POR_TU_APP.vercel.app
CSRF_TRUSTED_ORIGINS=https://CAMBIAR_POR_TU_APP.vercel.app,http://CAMBIAR_POR_IP_EC2:8090
ENVEOF

echo ""
echo ">>> EDITA .env antes de continuar: nano /home/ubuntu/hackathon/.env"
echo ">>> Luego ejecuta: bash /home/ubuntu/hackathon/scripts/start.sh"
