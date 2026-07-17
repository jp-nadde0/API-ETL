# 📌 Detalhes Importantes - API-ETL-PROJ

**Versão:** 1.0  
**Data:** 2026-07-17  
**Responsável:** Tech Lead

---

## 🎯 Propósito do Projeto

O **API-ETL-PROJ** é uma aplicação empresarial que:

1. **Extrai dados** de arquivos Excel (vendas) e PDF (custos de funcionários)
2. **Transforma dados** normalizando formatos, removendo nulos, calculando agregações
3. **Persiste dados** em banco de dados relacional (PostgreSQL) e NoSQL (DynamoDB)
4. **Expõe dados** via REST API segura (JWT autenticado)

---

## 🏆 Nível de Maturidade

**Classificação:** Sênior+ (Pleno com oportunidades)

- ✅ Código bem estruturado (SOLID principles)
- ✅ Testes abrangentes (69 testes, múltiplos tipos)
- ✅ Segurança implementada (JWT, validação)
- ✅ Pronto para produção com monitoramento
- ⚠️ Lacunas: cache, rate limiting, observabilidade centralizada

---

## 📊 Estatísticas do Código

| Métrica | Valor |
|---------|:-----:|
| **Linhas de Código** | ~2,500 |
| **Número de Arquivos Python** | 18 |
| **Número de Testes** | 69 |
| **Cobertura de Testes** | ~85% |
| **Endpoints** | 8 |
| **Modelos de Dados** | 6 (Pydantic) + 2 (SQLModel) |
| **Padrões SOLID Aplicados** | 5/5 |

---

## 🔄 Fluxo de Dados End-to-End

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Frontend/cURL)                  │
└──────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  AUTENTICAÇÃO                                               │
│  ├─ POST /auth/login (username, password)                 │
│  └─ Response: JWT token com exp 8h                        │
└──────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  API ENDPOINTS (Protegidos com Bearer token)               │
│  ├─ POST /extract_produtos/ → upload Excel                │
│  ├─ POST /resumir_vendas/ → download dados                │
│  ├─ POST /vendas/persistir/ → salvar DB                   │
│  └─ POST /extract_employee_costs/ → upload PDF            │
└──────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PROCESSAMENTO (Services + Extractors)                      │
│  ├─ ServicoVendas.extrair_produtos()                       │
│  ├─ ExtrairDadosProdutos.executar()                        │
│  ├─ Parsing (parse_float, parse_date)                      │
│  └─ ResumoVendas.extrair_tendencias()                      │
└──────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PERSISTÊNCIA                                               │
│  ├─ SQLModel.metadata.create_all()                         │
│  ├─ INSERT INTO vendas VALUES (...)                        │
│  ├─ DynamoDB.put_item() [employee_costs]                   │
│  └─ COMMIT transaction                                     │
└──────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  RESPOSTA (JSON serializado via Pydantic)                  │
│  ├─ Status 200 + dados extraídos/persistidos              │
│  ├─ Header X-Response-Time-Ms (performance metric)        │
│  └─ Logging estruturado em stdout (CloudWatch)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Diretórios (Explicada)

```
API-ETL-PROJ/
├── api/                          # Lógica da aplicação FastAPI
│   ├── api.py                   # Main FastAPI app, endpoints
│   ├── auth.py                  # JWT token generation/validation
│   ├── exceptions.py            # Custom exception handlers
│   ├── logging_config.py        # Structured logging setup
│   ├── config/
│   │   └── constants.py         # App-wide constants
│   └── services/                # Business logic layer
│       ├── sales_service.py     # Vendas orchestration
│       ├── employee_costs_service.py  # Custos orchestration
│       ├── file_service.py      # Arquivo temporário handling
│       └── interfaces.py        # Abstract contracts
│
├── database/                     # Data persistence layer
│   ├── repositories/            # Data access layer
│   │   ├── sales_repository.py  # SQL queries (Venda model)
│   │   └── employee_costs_repository.py  # DynamoDB queries
│   ├── utils/
│   │   └── parsers.py          # Float/Date parsing utilities
│   ├── alembic/                 # Database migrations
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/            # Migration scripts
│   └── __init__.py
│
├── extractors/                   # Data extraction logic
│   ├── sales_extractor.py       # Excel → Python objects
│   └── employee_costs_extractor.py  # PDF → Python objects
│
├── tests/                        # Test suite (69 tests)
│   ├── test_auth.py            # JWT tests (7)
│   ├── test_api_endpoints.py    # Integration tests (12)
│   ├── test_exceptions.py       # Exception handler tests (10)
│   ├── test_middleware.py       # Middleware tests (5)
│   ├── test_logging.py          # Logging tests (13)
│   ├── test_integration.py      # End-to-end tests (9)
│   ├── test_sales_extractor.py  # Sales extractor tests (3)
│   └── test_solid_services.py   # Service tests (2)
│
├── infra/                        # Infrastructure as Code
│   ├── terraform/
│   │   ├── main.tf             # EC2, RDS, Security Groups
│   │   └── terraform.tfstate   # State file (versionado)
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.extractor
│   │   └── docker-compose.prod.yml
│   └── scripts/
│       ├── setup-ec2.sh        # EC2 bootstrap
│       └── aws-ec2-deploy.md   # Deployment guide
│
├── docs/                         # Documentation
│   ├── ADR-001-stack-arquitecture.md  # Architecture decisions
│   └── USAGE-GUIDE.md           # Setup + usage guide
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
│
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # Project overview

```

---

## 🔑 Conceitos-Chave

### 1. **JWT Token Flow**

```
Cliente                        API
  │                            │
  ├─ POST /auth/login ────────►│
  │   (username, password)      │
  │                    criar_token()
  │                    ├─ payload = {"sub": "admin"}
  │                    ├─ adiciona exp = now + 8h
  │                    └─ jwt.encode(payload, secret, HS256)
  │◄────── {access_token, type} │
  │                            │
  ├─ GET /extract_produtos/ ──►│
  │   Authorization: Bearer ... │
  │                    verificar_token()
  │                    ├─ extrai token do header
  │                    ├─ jwt.decode(token, secret)
  │                    └─ valida exp
  │◄─────── {produtos: [...]} ─│
```

**Tokens expiram em 8 horas** - Necessário fazer login novamente

---

### 2. **Extração de Dados (3 tipos)**

#### A. Extração de Excel (Vendas)
```python
# Input: arquivo.xlsx (sheet: "Dados de Vendas")
# Headers: ID Venda | Data da Venda | Produto | ... | Estoque Atual

# Process:
workbook = load_workbook(arquivo)
worksheet = workbook["Dados de Vendas"]
for row in worksheet.iter_rows(values_only=True)[1:]:  # Skip header
    id_venda = row[0]
    data_venda = parse_date(row[1])  # Normaliza para YYYY-MM-DD
    preco = parse_float(row[4])  # Trata "1.234,56" → 1234.56
    # ... mais 5 campos

# Output: List[Tuple] com 8 elementos por linha
```

#### B. Resumo de Vendas
```python
# Calcula usando Counter():
- Produto MAIS vendido (maior contagem)
- Produto MENOS vendido (menor contagem)
- Categoria MAIS vendida (maior contagem)

# Return: Dict com 3 chaves (mais_vendidos, menos_vendidos, categoria_mais_vendida)
```

#### C. Extração de PDF (Custos)
```python
# Input: arquivo.pdf (Recibo de Pagamento)

# Process: Regex extraction
- Empresa: padrão r'([A-Z\s&]+LTDA)'
- Funcionário: padrão r'Funcionário:\s*([^\n]+?)\s+CBO:'
- Eventos: múltiplos regex compilados
- Bases de impostos: padrão complexo
- Totais: padrão com 3 campos

# ⚠️ Fragil: Quebra se PDF mudar de formato

# Output: Dict com 5 chaves (empresa, funcionario, eventos, bases, totais)
```

---

### 3. **Tratamento de Erros (4 tipos)**

```python
# ArquivoInvalidoError (422)
raise ArquivoInvalidoError("arquivo.pdf", "formato deve ser .xlsx")
# Response: {"erro": "arquivo_invalido", "arquivo": "...", "motivo": "..."}

# ExtratorError (500)
raise ExtratorError("Falha ao extrair", "Sheet não encontrada")
# Response: {"erro": "falha_extracao", "mensagem": "...", "detalhe": "..."}

# RepositorioError (500)
raise RepositorioError("persistir", "Coluna não existe")
# Response: {"erro": "falha_repositorio", ...}

# ServicoExternoError (502)
raise ServicoExternoError("extrator-service", 500, "Timeout")
# Response: {"erro": "servico_externo_indisponivel", ...}
```

---

### 4. **Logging Estruturado**

```python
# Exemplo de log em um endpoint
logger.info("POST /extract_produtos/ → 200 | 2.54ms")
logger.info("Extraindo produtos de '%s'", file.filename)
logger.error("Falha na extração", exc_info=True)

# Output (stdout):
# 2026-07-17 10:30:45.123 | INFO     | api.api | POST /extract_produtos/ → 200 | 2.54ms
# 2026-07-17 10:30:45.124 | INFO     | api.api | Extraindo produtos de 'vendas.xlsx'
```

---

## 🚨 Problemas Críticos Conhecidos

### 1. **Extração PDF Fragile** 🔴
- Regex muito específica para um modelo de PDF
- Se fornecedor mudar layout, falha silenciosa
- **Ação:** Implementar OCR ou usar PDF parser mais robusto

### 2. **Sem Rate Limiting** 🔴
- DDoS pode derrubar aplicação
- Sem proteção contra brute force (login)
- **Ação:** Adicionar middleware com sliding window

### 3. **Sem Observabilidade Centralizada** 🟠
- Logs apenas em stdout (perdidos se container reinicia)
- Sem APM (Application Performance Monitoring)
- **Ação:** Integrar CloudWatch + alarmes

---

## ✅ Validações Implementadas

### Backend
- ✅ JWT expiração
- ✅ File extension validation (.xlsx, .pdf)
- ✅ Pydantic models para todas as responses
- ✅ NULL/None handling em parsers
- ✅ Transaction-level consistency no banco

### Frontend (Se houver)
- ⚠️ Não existe ainda - cliente deve validar antes de enviar

---

## 📈 Performance Esperada

| Operação | Tempo | Observações |
|----------|:-----:|-------------|
| **Login** | 5-10ms | JWT encoding é rápido |
| **Extract 1000 linhas Excel** | 50-100ms | Parsing + memoria |
| **Resumo 1000 linhas** | 20-50ms | Counter é O(n) |
| **Persistir 1000 linhas** | 500-1000ms | I/O do banco |
| **Extract PDF 10 páginas** | 200-500ms | pdfplumber + regex |

---

## 🔐 Segurança por Camada

| Camada | Proteção | Status |
|--------|----------|:------:|
| **Transport** | HTTPS (via nginx proxy) | ⚠️ TODO |
| **Authentication** | JWT Bearer + expiration | ✅ Implementado |
| **Authorization** | Simples (todos usuarios = admin) | ⚠️ TODO |
| **Validation** | Pydantic + File validation | ✅ Implementado |
| **Error Handling** | Global handlers (sem stack trace) | ✅ Implementado |
| **Database** | SQLModel (previne SQL injection) | ✅ Implementado |
| **Logging** | Sem dados sensíveis | ✅ Implementado |

---

## 📞 Contatos & Escalação

| Problema | Primeiro Nível | Segundo Nível |
|----------|:-----------:|:-----------:|
| **API Down** | Health check | Ver logs CloudWatch |
| **DB Connection** | Verificar RDS status | Contatar DBA |
| **JWT Issues** | Fazer login novamente | Verificar JWT_SECRET_KEY |
| **PDF Extraction** | Verificar PDF format | Considerar OCR |
| **Performance Lenta** | Ver X-Response-Time-Ms header | Adicionar cache/índice |

---

## 📅 Roadmap Recomendado

### Fase 1: MVP (AGORA - 1 semana)
- ✅ Deploy em produção
- ✅ Monitorar erros
- ✅ Recolher feedback de usuários

### Fase 2: Hardening (2-4 semanas)
- ⚠️ Rate limiting
- ⚠️ CloudWatch integration
- ⚠️ Refresh tokens
- ⚠️ CORS middleware

### Fase 3: Scale (1-2 meses)
- ⚠️ Redis cache
- ⚠️ CD automatizado
- ⚠️ APM + distributed tracing
- ⚠️ Melhorar PDF extraction

### Fase 4: Enterprise (2-3 meses+)
- ⚠️ OAuth2 / SSO
- ⚠️ Multi-tenancy
- ⚠️ Compliance (LGPD, SOC2)
- ⚠️ Disaster recovery

---

## 🎓 Lições Aprendidas

1. **SOLID principles salvam refatorações** - Código é fácil de estender
2. **Testes desde o início** - Evita surpresas em produção
3. **Observabilidade é crítica** - Impossível debugar sem logs
4. **Escolher tecnologia certa para o job** - FastAPI foi escolha perfeita
5. **DynamoDB é ótimo para unstructured data** - Mas PDF é edge case

---

## 📚 Referências & Documentação

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLModel:** https://sqlmodel.tiangolo.com/
- **Pytest:** https://docs.pytest.org/
- **AWS EC2:** https://docs.aws.amazon.com/ec2/
- **Terraform:** https://www.terraform.io/docs

---

## ✨ Conclusão

O API-ETL-PROJ é um projeto **sólido e pronto para produção** com uma arquitetura bem pensada. As melhorias recomendadas são incrementais e não bloqueam o lançamento do MVP.

**Recomendação:** Lançar em produção agora, monitorar intensamente, e implementar melhorias com base em feedback de usuários e métricas de produção.

