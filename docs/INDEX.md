# 📚 Índice de Documentação - API-ETL-PROJ

**Data:** 2026-07-17  
**Versão:** 1.0  

---

## 🎯 Visão Geral

Este índice centraliza toda a documentação do projeto API-ETL-PROJ. Use para navegar rapidamente até o tópico que precisa.

---

## 📖 Documentação Principal

### 1. [ADR-001: Stack e Arquitetura](docs/ADR-001-stack-arquitecture.md)
**Para:** Arquitetos, Tech Leads, Decision Makers

**Conteúdo:**
- ✅ Stack escolhido (FastAPI, PostgreSQL, DynamoDB, Terraform, Docker)
- ✅ Por que cada tecnologia foi escolhida
- ✅ Alternativas descartadas
- ✅ Pontos fortes do projeto (8 categorias)
- ✅ Pontos fracos e críticos (10 problemas)
- ✅ Roadmap recomendado (4 fases)

**Tempo de Leitura:** 15-20 min

---

### 2. [USAGE-GUIDE: Guia de Uso](docs/USAGE-GUIDE.md)
**Para:** Developers, DevOps, System Administrators

**Conteúdo:**
- ✅ Setup local passo-a-passo
- ✅ Como usar a API via cURL
- ✅ Deploy em AWS com Terraform
- ✅ Uso em produção (health checks, logs, backups)
- ✅ Endpoints disponíveis
- ✅ Variáveis de ambiente
- ✅ Troubleshooting detalhado
- ✅ Arquitetura de banco de dados

**Tempo de Leitura:** 20-30 min

**Seções Principais:**
1. [Requisitos](#requisitos) - O que você precisa
2. [Setup Local](#setup-local) - 6 passos
3. [Usar Localmente](#usar-localmente) - Exemplos de uso
4. [Deploy em Produção](#deploy-em-produção-aws) - Terraform
5. [Usar em Produção](#usar-em-produção) - Health checks
6. [Troubleshooting](#troubleshooting) - Soluções comuns
7. [Endpoints](#endpoints-disponíveis) - Referência rápida
8. [Variáveis de Ambiente](#variáveis-de-ambiente) - Por ambiente

---

### 3. [IMPORTANT-DETAILS: Detalhes Críticos](docs/IMPORTANT-DETAILS.md)
**Para:** Todos (referência técnica contínua)

**Conteúdo:**
- ✅ Propósito do projeto
- ✅ Nível de maturidade (Sênior+)
- ✅ Estatísticas de código
- ✅ Fluxo de dados end-to-end (diagrama)
- ✅ Estrutura de diretórios (com explicações)
- ✅ Conceitos-chave (JWT, extração, logging)
- ✅ Problemas críticos conhecidos
- ✅ Validações implementadas
- ✅ Performance esperada
- ✅ Segurança por camada
- ✅ Roadmap detalhado

**Tempo de Leitura:** 25-35 min

---

## 🔗 Documentação Complementar

### No Repositório
| Arquivo | Propósito | Público |
|---------|-----------|:-------:|
| `README.md` | Visão geral do projeto | ✅ |
| `.env.example` | Variáveis de ambiente | ✅ |
| `pytest.ini` | Configuração de testes | 🔍 |
| `requirements.txt` | Dependências Python | ✅ |
| `.gitignore` | Arquivos ignorados | ✅ |

### Na AWS
| Recurso | Documentação | Link |
|---------|-------------|:----:|
| EC2 | Instance details | AWS Console |
| RDS | Database info | AWS Console |
| ECR | Repository URIs | AWS Console |
| CloudWatch | Logs | AWS Console |

### Externo
| Ferramenta | Documentação | Link |
|-----------|-------------|:----:|
| FastAPI | Official docs | https://fastapi.tiangolo.com |
| SQLModel | ORM guide | https://sqlmodel.tiangolo.com |
| Terraform | IaC guide | https://www.terraform.io |
| Docker | Container guide | https://docs.docker.com |

---

## 🎓 Guias por Casos de Uso

### "Quero começar a usar a API localmente"
1. Ler: [Setup Local](#setup-local) em USAGE-GUIDE
2. Executar: Passos 1-6
3. Teste: `curl http://localhost:8000/health`
4. Explore: http://localhost:8000/docs (Swagger)

**Tempo:** 15 min

---

### "Quero fazer deploy em produção"
1. Ler: [Deploy em Produção](#deploy-em-produção-aws) em USAGE-GUIDE
2. Ler: Seção "Segurança em Produção" em IMPORTANT-DETAILS
3. Executar: Passos 1-6 de Deploy
4. Monitorar: CloudWatch logs

**Tempo:** 1-2 horas

---

### "Quero entender a arquitetura"
1. Ler: [ADR-001](#adr-001-stack-e-arquitetura) inteiro
2. Ler: [Fluxo de Dados](#fluxo-de-dados-end-to-end) em IMPORTANT-DETAILS
3. Ler: [Estrutura de Diretórios](#estrutura-de-diretórios) em IMPORTANT-DETAILS
4. Revisar: Código em `api/`, `database/`, `extractors/`

**Tempo:** 1-2 horas

---

### "Quero debugar um problema em produção"
1. Ir para: [Troubleshooting](#troubleshooting) em USAGE-GUIDE
2. Se não encontrado, ler: [Problemas Críticos](#problemas-críticos-conhecidos) em IMPORTANT-DETAILS
3. Verificar: Logs em CloudWatch
4. Se persistir: Ler stack trace + revisar código

**Tempo:** 15-30 min

---

### "Quero adicionar um novo endpoint"
1. Revisar: [Arquitetura SOLID](#arquitetura-solid) em ADR-001
2. Revisar: [Estrutura de Diretórios](#estrutura-de-diretórios-explicada) em IMPORTANT-DETAILS
3. Seguir padrão:
   - Criar extrator em `extractors/`
   - Criar service em `api/services/`
   - Criar endpoint em `api/api.py`
   - Adicionar teste em `tests/`
4. Rodar: `pytest tests/ -v`

**Tempo:** 1-2 horas

---

## 📊 Quick Reference

### Endpoints (Referência Rápida)
```bash
# Health check (sem auth)
GET /health

# Login (obter token)
POST /auth/login

# Extrair vendas (com token)
POST /extract_produtos/

# Resumir vendas (com token)
POST /resumir_vendas/

# Persistir vendas (com token)
POST /vendas/persistir/

# Extrair custos (com token)
POST /extract_employee_costs/

# Documentação Swagger
GET /docs
```

---

### Comandos Úteis
```bash
# Rodar testes localmente
pytest tests/ -v

# Iniciar servidor local
uvicorn api.api:app --reload

# Build Docker image
docker build -f infra/docker/Dockerfile.api -t api-etl-api:latest .

# Deploy com Terraform
cd infra/terraform && terraform apply

# Ver logs em produção
docker logs -f api-etl-api-1

# SSH em EC2
ssh -i "api-etl-nginx-key.pem" ubuntu@<IP>

# Fazer login na API
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

### Estrutura de Diretórios (Alta Nível)
```
API-ETL-PROJ/
├── api/              # FastAPI application
├── database/         # Data access layer
├── extractors/       # Data extraction
├── tests/            # Test suite (69 testes)
├── infra/            # Infrastructure as Code
│   ├── terraform/    # Terraform configs
│   ├── docker/       # Dockerfiles
│   └── scripts/      # Deployment scripts
├── docs/             # Documentação (este arquivo)
└── requirements.txt  # Python dependencies
```

---

### Variáveis de Ambiente Críticas
```bash
# SEMPRE necessário
JWT_SECRET_KEY=sua-chave-secreta-produção

# SEMPRE necessário
DATABASE_URL=postgresql://user:pass@host:5432/db

# Opcional (padrão: http://localhost:5000/processar)
EXTRACTOR_URL=http://extractor-service:5000/processar

# Opcional (padrão: INFO)
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
```

---

## 🆘 Help & Support

### Perguntas Frequentes

**P: Como obter um token JWT?**
A: Fazer POST em `/auth/login` com username e password. Token expira em 8h.

**P: Qual é a senha padrão?**
A: `username: admin`, `password: admin123` (só para desenvolvimento!)

**P: Posso usar com múltiplos usuários?**
A: Não ainda. Implementar OAuth2/Cognito futuramente.

**P: O PDF extraction sempre falha. Por quê?**
A: É fragile. Requer formato específico de PDF. Solução: OCR (futuro).

**P: Como adicionar Redis cache?**
A: Referência: [Roadmap - Médio Prazo](#médio-prazo-primeiras-2-4-semanas)

---

### Onde Obter Ajuda

| Problema | Lugar | Ação |
|----------|:-----:|:----:|
| Setup local quebrado | USAGE-GUIDE [Troubleshooting](#troubleshooting) | Seguir step-by-step |
| Deploy falha | ADR-001 + USAGE-GUIDE | Verificar logs |
| API retorna 401 | IMPORTANT-DETAILS [JWT](#1-jwt-token-flow) | Fazer login novamente |
| Performance lenta | IMPORTANT-DETAILS [Performance](#performance-esperada) | Verificar header X-Response-Time-Ms |
| Quer escalabilidade | ADR-001 [Roadmap](#roadmap-recomendado) | Implementar fase 3 |

---

## 📈 Estatísticas do Projeto

| Métrica | Valor |
|---------|:-----:|
| **Stack Score** | 7.75/10 |
| **Testes** | 69 (85% cobertura) |
| **Linhas de Código** | ~2,500 |
| **Endpoints** | 8 |
| **Modelos de Dados** | 8 |
| **Documentação** | 4,000+ linhas |

---

## ✅ Checklist de Deploy

- [ ] Ler [ADR-001](#adr-001-stack-e-arquitetura)
- [ ] Seguir [Setup Local](#setup-local)
- [ ] Rodar todos os testes: `pytest tests/ -v`
- [ ] Revisar [Segurança](#-segurança-por-camada) em IMPORTANT-DETAILS
- [ ] Seguir [Deploy em Produção](#deploy-em-produção-aws)
- [ ] Configurar CloudWatch logs
- [ ] Implementar health check monitoring
- [ ] Testar todos endpoints em produção
- [ ] Documentar secrets em AWS Secrets Manager

---

## 🚀 Próximos Passos

1. **Agora:** Deploy MVP em produção
2. **Semana 1:** Monitorar e recolher feedback
3. **Semana 2-4:** Implementar [Hardening](#fase-2-hardening-2-4-semanas)
4. **Semana 5+:** Roadmap de escala

---

## 📝 Versionamento da Documentação

| Versão | Data | Mudanças |
|--------|:----:|----------|
| 1.0 | 2026-07-17 | Documentação inicial |
| - | - | - |

---

## 📞 Contato

Para dúvidas ou atualizações nesta documentação, favor contatar:
- Tech Lead: [seu-email]
- DBA: [seu-email]
- DevOps: [seu-email]

---

**Última Atualização:** 2026-07-17  
**Proxima Review:** 2026-08-17

