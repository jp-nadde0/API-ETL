# Deploy na AWS Free Tier

## 1. Criar instância EC2
- Tipo: t3.micro
- AMI: Ubuntu Server 22.04 LTS
- Segurança: liberar portas 22, 80, 8000, 5000
- Storage: 20 GB

## 2. Conectar na instância
```bash
ssh -i sua-chave.pem ubuntu@<public-ip>
```

## 3. Instalar Docker e Docker Compose
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
newgrp docker
```

## 4. Clonar o projeto
```bash
cd /home/ubuntu
git clone <repo-url>
cd API-ETL-PROJ
```

## 5. Configurar o banco RDS PostgreSQL
- Engine: PostgreSQL
- Instance class: db.t3.micro
- Storage: 20 GB
- Public access: sim (ou use subnet/private access se preferir)
- Liberar porta 5432 no security group

## 6. Definir variável de ambiente
```bash
export DATABASE_URL="postgresql+psycopg2://<user>:<password>@<rds-endpoint>:5432/<db>"
```

## 7. Subir os containers
```bash
docker compose up -d --build
```

## 8. Verificar saúde
```bash
docker compose ps
curl http://localhost:8000/docs
curl http://localhost:5000/health
```
