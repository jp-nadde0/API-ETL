#!/bin/bash
set -e

echo "Atualizando pacotes..."
sudo apt update
sudo apt upgrade -y

echo "Instalando Docker..."
sudo apt install -y docker.io docker-compose-plugin git

echo "Iniciando Docker..."
sudo systemctl enable docker
sudo systemctl start docker

echo "Adicionando usuário ao grupo docker..."
sudo usermod -aG docker ubuntu
newgrp docker

echo "Clonando repositório..."
cd /home/ubuntu
git clone <URL_DO_SEU_REPOSITORIO> api-etl-proj
cd api-etl-proj

echo "Criando arquivo .env..."
cp .env.example .env

echo "Atualizando arquivo .env com credenciais da AWS..."
echo ""
echo "Edite o arquivo .env com os dados do RDS e DynamoDB:"
echo "  DATABASE_URL=postgresql+psycopg2://usuario:senha@rds-endpoint:5432/appdb"
echo "  AWS_REGION=us-east-1"
echo "  AWS_ENDPOINT_URL=http://dynamodb:8001 (ou deixe em branco se usar AWS real)"
echo ""

echo "Iniciando containers..."
docker compose up -d --build

echo "Aguardando inicialização..."
sleep 10

echo "Verificando status dos containers..."
docker compose ps

echo "Setup completo!"
echo "API disponível em: http://localhost:8000/docs"
echo "Extrator disponível em: http://localhost:5000/health"
