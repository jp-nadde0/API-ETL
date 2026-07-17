# 📖 Guia Completo de Uso - API-ETL-PROJ

**Versão:** 1.0  
**Data:** 2026-07-17  
**Última Atualização:** 2026-07-17

---

## 📑 Índice

1. [Requisitos](#requisitos)
2. [Setup Local](#setup-local)
3. [Usar Localmente](#usar-localmente)
4. [Deploy em Produção (AWS)](#deploy-em-produção-aws)
5. [Usar em Produção](#usar-em-produção)
6. [Troubleshooting](#troubleshooting)
7. [Arquitetura de Banco de Dados](#arquitetura-de-banco-de-dados)
8. [Endpoints Disponíveis](#endpoints-disponíveis)
9. [Variáveis de Ambiente](#variáveis-de-ambiente)
10. [Segurança](#segurança)

---

## 🔧 Requisitos

### Desenvolvimento Local
- **Python 3.13+** (pode usar 3.11)
- **Docker 24.0+** (opcional, para usar containers localmente)
- **Git**
- **VSCode** (recomendado) ou outro editor

### Produção (AWS)
- **Conta AWS** com credenciais configuradas
- **EC2** (t3.micro recomendado)
- **RDS PostgreSQL** (db.t3.micro recomendado)
- **ECR** (Elastic Container Registry)
- **Terraform 1.15+**

---

## 🏠 Setup Local

### Passo 1: Clonar Repositório
```bash
git clone https://github.com/seu-user/API-ETL-PROJ.git
cd API-ETL-PROJ
```

### Passo 2: Criar e Ativar Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

**Dependências principais:**
- `fastapi==0.138.2` - Framework web assíncrono
- `uvicorn==0.49.0` - Servidor ASGI
- `sqlmodel==0.0.39` - ORM com validação Pydantic
- `pydantic==2.13.4` - Validação de dados
- `python-jose==3.5.0` - JWT
- `pytest==9.1.1` - Testes
- `alembic==1.18.5` - Migrações de banco

### Passo 4: Configurar Variáveis de Ambiente

Criar arquivo `.env` na raiz (copiar de `.env.example`):
```bash
cp .env.example .env
```

**Conteúdo do `.env` (desenvolvimento):**
```bash
# Autenticação
JWT_SECRET_KEY=sua-chave-super-secreta-desenvolvimento

# Banco de Dados
DATABASE_URL=sqlite:///sales.db  # SQLite local (padrão)
# OU para PostgreSQL local:
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/api_etl_db

# Extractor Service
EXTRACTOR_URL=http://localhost:5000/processar  # Local ou remoto

# Logging
LOG_LEVEL=INFO
```

### Passo 5: Rodar Testes Localmente
```bash
pytest tests/ -v
```

**Output esperado:**
```
============================= 69 passed in 2.50s ==============================
```

Se algum teste falhar, verifique a seção [Troubleshooting](#troubleshooting).

### Passo 6: Iniciar Servidor Local
```bash
uvicorn api.api:app --reload --host 0.0.0.0 --port 8000
```

**Output esperado:**
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🚀 Usar Localmente

### Acessar Swagger Documentation
```
http://localhost:8000/docs
```

### Acessar OpenAPI JSON Schema
```
http://localhost:8000/openapi.json
```

### Health Check (Sem autenticação)
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status": "ok"}
```

### 1. Fazer Login e Obter JWT Token

**Credenciais padrão:**
- Username: `admin`
- Password: `admin123`

**Via cURL:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Salvar token (PowerShell):**
```powershell
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Salvar token (Bash):**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 2. Extrair Produtos de Arquivo Excel

**Preparar arquivo Excel:**
1. Abrir Excel
2. Criar aba chamada "Dados de Vendas"
3. Headers: `ID Venda | Data da Venda | Produto | Categoria | Preço Unitário | Quantidade Vendida | Estoque Atual`
4. Adicionar dados
5. Salvar como `vendas.xlsx`

**Via cURL (Windows PowerShell):**
```powershell
$TOKEN = "seu-token-aqui"
curl -X POST http://localhost:8000/extract_produtos/ `
  -H "Authorization: Bearer $TOKEN" `
  -F "file=@vendas.xlsx"
```

**Via cURL (Linux/Mac):**
```bash
TOKEN="seu-token-aqui"
curl -X POST http://localhost:8000/extract_produtos/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@vendas.xlsx"
```

**Response:**
```json
{
  "produtos": [
    [1, "2023-01-15", "Produto A", "Eletrônicos", 99.99, 5, 1234.56, 100],
    [2, "2023-01-16", "Produto B", "Alimentos", 29.90, 10, 755.00, 200]
  ]
}
```

---

### 3. Resumir Vendas

**Via cURL:**
```bash
curl -X POST http://localhost:8000/resumir_vendas/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@vendas.xlsx"
```

**Response:**
```json
{
  "resumo": {
    "mais_vendidos": [
      {"produto": "Produto B", "quantidade": 3}
    ],
    "menos_vendidos": [
      {"produto": "Produto A", "quantidade": 1}
    ],
    "categoria_mais_vendida": {
      "categoria": "Alimentos",
      "quantidade": 2
    }
  }
}
```

---

### 4. Persistir Vendas em Banco de Dados

**Via cURL:**
```bash
curl -X POST http://localhost:8000/vendas/persistir/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@vendas.xlsx"
```

**Response:**
```json
{
  "persistidos": 2,
  "database_url": "sqlite:///sales.db"
}
```

**Verificar dados no banco (SQLite):**
```bash
sqlite3 sales.db "SELECT * FROM vendas LIMIT 10;"
```

---

### 5. Extrair Custos de Funcionários (PDF)

**Preparar PDF:**
- Deve estar no formato de "Recibo de Pagamento" da Nexus Tech
- Conter seções: Empresa, Funcionário, Eventos, Bases de Impostos, Totais

**Via cURL:**
```bash
curl -X POST http://localhost:8000/extract_employee_costs/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@recibo.pdf"
```

**Response:**
```json
{
  "empresa": {
    "nome": "NEXUS TECH & RETAIL LTDA",
    "cnpj": "12.345.678/0001-99",
    "inscricao_estadual": "123.456.789.123",
    "data_periodo": "01/2023"
  },
  "funcionario": {
    "codigo": "12345",
    "nome": "João Silva",
    "cbo": "2123-45",
    "funcao": "Assistente de RH"
  },
  "eventos": [
    {"codigo": "101", "descricao": "Salário Base", "referencia": "30", "provento": 3000.00},
    {"codigo": "102", "descricao": "INSS", "referencia": "11%", "desconto": 330.00}
  ],
  "bases_impostos": {
    "base_inss": 3000.00,
    "base_irrf": 2670.00,
    "base_fgts": 3000.00,
    "fgts_mes": 240.00
  },
  "totais": {
    "total_proventos": 3000.00,
    "total_descontos": 330.00,
    "total_liquido": 2670.00
  }
}
```

---

## 🌐 Deploy em Produção (AWS)

### Pré-requisitos
- AWS CLI configurado localmente
- Terraform instalado
- Conta AWS com permissões de EC2, RDS, ECR

### Passo 1: Preparar Credenciais AWS
```bash
aws configure

# Será solicitado:
# AWS Access Key ID: ...
# AWS Secret Access Key: ...
# Default region: us-east-1
# Default output format: json
```

### Passo 2: Criar ECR Repository
```bash
aws ecr create-repository --repository-name api-etl-api --region us-east-1
aws ecr create-repository --repository-name api-etl-extrator --region us-east-1
```

**Output:** Anote a URL do repositório (ex: `847564370007.dkr.ecr.us-east-1.amazonaws.com`)

### Passo 3: Build e Push de Docker Images

**Fazer Login no ECR:**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 847564370007.dkr.ecr.us-east-1.amazonaws.com
```

**Build API Image:**
```bash
docker build -f infra/docker/Dockerfile.api \
  -t 847564370007.dkr.ecr.us-east-1.amazonaws.com/api-etl-api:latest .
```

**Build Extractor Image:**
```bash
docker build -f infra/docker/Dockerfile.extractor \
  -t 847564370007.dkr.ecr.us-east-1.amazonaws.com/api-etl-extrator:latest .
```

**Push para ECR:**
```bash
docker push 847564370007.dkr.ecr.us-east-1.amazonaws.com/api-etl-api:latest
docker push 847564370007.dkr.ecr.us-east-1.amazonaws.com/api-etl-extrator:latest
```

### Passo 4: Provisionar Infraestrutura com Terraform

**Configurar variables (infra/terraform/terraform.tfvars):**
```hcl
aws_region            = "us-east-1"
environment           = "production"
instance_type         = "t3.micro"
db_instance_class     = "db.t3.micro"
db_username           = "admin"
db_password           = "sua-senha-super-secreta"  # ⚠️ Usar AWS Secrets Manager em produção
```

**Inicializar Terraform:**
```bash
cd infra/terraform
terraform init
terraform plan  # Revisar o que será criado
terraform apply # Confirmar com 'yes'
```

**Output:** Anote os outputs (IP da EC2, endpoint do RDS)

### Passo 5: Configurar Banco de Dados em Produção

**Conectar à EC2 via SSH:**
```bash
ssh -i "api-etl-nginx-key.pem" ubuntu@<IP-da-EC2>
```

**Nas variáveis de ambiente da EC2 (em `/etc/systemd/system/api-etl.service`):**
```bash
Environment="DATABASE_URL=postgresql://admin:senha@api-etl-rds.csnecs2wiv4k.us-east-1.rds.amazonaws.com:5432/api_etl_db"
Environment="JWT_SECRET_KEY=sua-chave-muito-secreta-producao"
Environment="EXTRACTOR_URL=http://localhost:5000/processar"
```

### Passo 6: Iniciar Containers em Produção

**Na EC2, criar docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  api:
    image: 847564370007.dkr.ecr.us-east-1.amazonaws.com/api-etl-api:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://admin:senha@rds-endpoint:5432/api_etl_db
      - JWT_SECRET_KEY=sua-chave-producao
    restart: always

  extractor:
    image: 847564370007.dkr.ecr.us-east-1.amazonaws.com/api-etl-extrator:latest
    ports:
      - "5000:5000"
    restart: always
```

**Iniciar containers:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔒 Usar em Produção

### URL de Produção
```
https://api-etl.seu-dominio.com  (com nginx reverse proxy)
OU
http://<IP-EC2>:8000  (acesso direto)
```

### 1. Login (Produção)
```bash
curl -X POST https://api-etl.seu-dominio.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Health Check (Monitoramento)
```bash
curl https://api-etl.seu-dominio.com/health
```

**Configure em seu monitoramento (CloudWatch, Datadog):**
```bash
# Executar a cada 5 minutos
*/5 * * * * curl -f https://api-etl.seu-dominio.com/health || alert "API Down"
```

### 3. Logs em Produção

**Ver logs da API:**
```bash
docker logs -f api-etl-api-1
```

**Ver logs estruturados (CloudWatch):**
```bash
aws logs tail /aws/ec2/api-etl-api --follow
```

### 4. Backups de Banco de Dados

**Backup automático via RDS (configurado via Terraform):**
- Retenção de 7 dias
- Backup diário a 02:00 UTC

**Backup manual:**
```bash
pg_dump -h api-etl-rds.csnecs2wiv4k.us-east-1.rds.amazonaws.com \
  -U admin \
  -d api_etl_db \
  > backup-$(date +%Y%m%d).sql
```

---

## 🐛 Troubleshooting

### Problema 1: "ModuleNotFoundError: No module named 'jose'"
**Solução:**
```bash
pip install python-jose[cryptography]
```

### Problema 2: "JWT token is invalid or expired" (401)
**Causas possíveis:**
1. Token expirado (8 horas)
2. JWT_SECRET_KEY incorreta
3. Bearer token malformado

**Solução:**
```bash
# Fazer login novamente
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Problema 3: "database is locked" (SQLite)
**Causa:** SQLite não suporta múltiplas conexões simultâneas

**Solução:** Usar PostgreSQL em produção
```bash
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Problema 4: PDF extraction retorna campos vazios
**Causa:** Formato de PDF diferente do esperado

**Solução:**
1. Verificar se PDF está no formato "Recibo de Pagamento" Nexus Tech
2. Verificar se todas as seções (Empresa, Funcionário, etc) estão presentes
3. Usar pytesseract para OCR se PDF for scaneado

### Problema 5: Port 8000 already in use
**Solução (Windows):**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Solução (Linux/Mac):**
```bash
lsof -i :8000
kill -9 <PID>
```

### Problema 6: "Permission denied" ao SSH na EC2
**Solução:**
```bash
# Verificar permissões da chave
chmod 600 api-etl-nginx-key.pem

# Tentar conexão novamente
ssh -i api-etl-nginx-key.pem ubuntu@<IP>
```

---

## 🗄️ Arquitetura de Banco de Dados

### Schema SQLModel
```sql
CREATE TABLE vendas (
  id SERIAL PRIMARY KEY,
  id_venda INTEGER NOT NULL,
  data_venda DATE,
  produto VARCHAR NOT NULL,
  categoria VARCHAR,
  preco_unitario FLOAT,
  quantidade_vendida FLOAT,
  faturamento_total FLOAT,
  estoque_atual FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendas_produto ON vendas(produto);
CREATE INDEX idx_vendas_data ON vendas(data_venda);
```

### DynamoDB (Employee Costs)
```
Table: employee_costs
Primary Key: funcionario_id (String)
Attributes:
  - empresa_cnpj
  - data_periodo
  - eventos (List)
  - totais (Map)
  - created_at
  - updated_at
```

### Migrações com Alembic
```bash
# Gerar nova migration
alembic revision --autogenerate -m "Add vendas table"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1
```

---

## 📡 Endpoints Disponíveis

| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/docs` | ❌ | Swagger UI |
| `GET` | `/openapi.json` | ❌ | OpenAPI schema |
| `POST` | `/auth/login` | ❌ | Obter JWT token |
| `POST` | `/extract_produtos/` | ✅ | Extrair produtos de Excel |
| `POST` | `/resumir_vendas/` | ✅ | Resumir vendas (top/bottom) |
| `POST` | `/vendas/persistir/` | ✅ | Persistir vendas no banco |
| `POST` | `/extract_employee_costs/` | ✅ | Extrair custos de PDF |

---

## 🔐 Variáveis de Ambiente

### Desenvolvimento
```bash
JWT_SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///sales.db
EXTRACTOR_URL=http://localhost:5000/processar
LOG_LEVEL=DEBUG
```

### Produção
```bash
JWT_SECRET_KEY=<usar AWS Secrets Manager>
DATABASE_URL=postgresql://admin:SENHA@rds-endpoint:5432/api_etl_db
EXTRACTOR_URL=http://extractor-service:5000/processar
LOG_LEVEL=INFO
```

---

## 🛡️ Segurança

### Best Practices Implementadas
- ✅ JWT com expiração de 8 horas
- ✅ HTTPBearer validation
- ✅ Password hashing (USUARIOS dict é apenas para demo)
- ✅ Validação de arquivo por extensão
- ✅ Tratamento de erro global (sem stack traces)

### Best Practices Faltando
- ❌ Rate limiting
- ❌ CORS restritivo
- ❌ Secrets rotation
- ❌ SQL injection prevention (usar ORM - já implementado)

### Mudanças de Produção
```python
# ANTES (Desenvolvimento)
USUARIOS = {"admin": "admin123"}  # Hardcoded

# DEPOIS (Produção)
# Usar AWS Cognito ou Auth0
# Armazenar senhas em banco com bcrypt
# Implementar 2FA
```

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique o [ADR-001](docs/ADR-001-stack-arquitecture.md)
2. Revisar logs: `docker logs <container>`
3. Executar testes: `pytest tests/ -v`
4. Criar issue no GitHub com stack trace

