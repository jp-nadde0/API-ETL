# ADR-001: Decisões Arquiteturais da Stack API-ETL-PROJ

**Data:** 2026-07-17  
**Status:** Aceito  
**Decisor:** Arquitetura de Projeto  

---

## 📋 Contexto

O API-ETL-PROJ é uma aplicação empresarial para extrair, transformar e persistir dados de vendas e custos de funcionários. Necessita alta disponibilidade, segurança, escalabilidade e facilidade de manutenção em ambiente de nuvem (AWS).

---

## 🏗️ Stack Escolhido

### Backend: FastAPI 0.138.2
- **Por que:** Framework assíncrono de alto desempenho, integração automática com Swagger/OpenAPI, validação de dados nativa via Pydantic
- **Alternativas descartadas:** Django (overkill para API), Flask (muito básico)
- **Tradeoff:** Curva de aprendizado, menos ecossistema que Django

### Banco de Dados: PostgreSQL 16.3 (RDS)
- **Por que:** Relacional robusto, suporta transações ACID, escalável em cloud, gerenciado pela AWS
- **Alternativas descartadas:** SQLite (desenvolvimento), NoSQL (não necessário para estrutura tabular)
- **Tradeoff:** Custão na AWS, complexidade operacional

### Cache/Sessões: DynamoDB (for employee_costs)
- **Por que:** NoSQL escalável, pay-per-request, integra nativamente com AWS
- **Alternativas descartadas:** Redis (custo adicional), Cache local (não distribuído)
- **Tradeoff:** Lattency maior, menos queries complexas

### Containerização: Docker + ECR
- **Por que:** Portabilidade, isolamento, CI/CD automatizado, fácil deployment
- **Alternativas descartadas:** VMs (mais pesadas), Serverless (menos controle)
- **Tradeoff:** Overhead de container orchestration

### Infraestrutura: Terraform + EC2 + RDS
- **Por que:** IaC reproduzível, versionável, multi-ambiente suportado
- **Alternativas descartadas:** AWS CDK (mais verboso), CloudFormation (YAML verbose)
- **Tradeoff:** Curva de aprendizado, estado remoto necessário

### Autenticação: JWT (python-jose)
- **Por que:** Stateless, escalável, padrão da indústria, sem dependência de sessão
- **Alternativas descartadas:** OAuth2 (complexidade extra), API Key (menos seguro)
- **Tradeoff:** Tokens não podem ser revogados imediatamente, necessita refresh

### Logging: Logging nativo Python + estruturado
- **Por que:** Integração nativa, baixo overhead, estruturado para CloudWatch
- **Alternativas descartadas:** ELK Stack (complexidade), DataDog (custo)
- **Tradeoff:** Análise local limitada

### Testes: pytest + TestClient (FastAPI)
- **Por que:** Padrão Python, fixtures poderosas, integração com CI/CD
- **Alternativas descartadas:** unittest (mais verboso), behave (overkill)
- **Tradeoff:** Setup inicial mais complexo

---

## 💪 Pontos Fortes do Projeto

### 1. **Segurança em Nível Empresarial**
- ✅ JWT com expiração de 8 horas
- ✅ HTTPBearer validation em todos endpoints protegidos
- ✅ Tratamento de erro global (não expõe stack traces)
- ✅ Validação de arquivo por extensão

**Score:** 8/10 (Falta: rate limiting, CORS configurável, secrets manager)

### 2. **Arquitetura SOLID**
- ✅ Separação clara de responsabilidades (api/, database/, extractors/)
- ✅ Interfaces abstratas (RepositorioVendas, ExtratorVendas)
- ✅ Injeção de dependência em serviços
- ✅ Testes facilitados com mocks

**Score:** 8/10 (Falta: dependency injection completo em endpoints)

### 3. **Qualidade de Código**
- ✅ 69 testes cobrindo autenticação, exceções, middleware, logging, integração
- ✅ Sem redundâncias significativas
- ✅ Imports limpos e organizados
- ✅ Documentação de código via docstrings

**Score:** 8/10 (Falta: cobertura de 100%, mutation testing)

### 4. **Escalabilidade**
- ✅ Async/await em FastAPI (suporta 1000s de conexões simultâneas)
- ✅ Banco relacional escalável (RDS com read replicas possível)
- ✅ Containerização facilita horizontal scaling
- ✅ DynamoDB pay-per-request (escalabilidade automática)

**Score:** 8/10 (Falta: cache em memória, CDN para assets)

### 5. **Observabilidade**
- ✅ Logging estruturado em todos endpoints
- ✅ Performance metrics (X-Response-Time-Ms header)
- ✅ Swagger automático para documentação
- ✅ Rastreamento de operações

**Score:** 7/10 (Falta: APM, distributed tracing, alertas)

### 6. **DevOps & Automação**
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ IaC com Terraform (EC2, RDS, Security Groups)
- ✅ Docker multi-image (api, extractor)
- ✅ Alembic para migrações de banco (versionadas)

**Score:** 8/10 (Falta: CD automatizado, blue-green deployment)

### 7. **Robustez de Dados**
- ✅ Parsers tolerantes a múltiplos formatos (BR e EN)
- ✅ Tratamento de NULL/None em cadeia
- ✅ Validação Pydantic em endpoints
- ✅ Transações ACID no banco

**Score:** 8/10 (Falta: validação de business rules mais complexas)

### 8. **Documentação**
- ✅ Swagger automático (/docs, /openapi.json)
- ✅ README com setup
- ✅ Code comments explicativos
- ✅ ADR detalhado (este arquivo)

**Score:** 7/10 (Falta: guia de troubleshooting, diagramas de arquitetura)

---

## ⚠️ Pontos Fracos do Projeto

### 1. **Extração de PDF (Employee Costs) - Fragile** 🔴 CRÍTICO
- ❌ Regex muito específica para um modelo de PDF
- ❌ Se formato do PDF mudar, extração falha silenciosamente
- ❌ Sem validação de página ou verificação de estrutura
- ❌ Testes apenas com dados mock, não com PDFs reais

**Impacto:** Alto - Pode perder dados se fornecedor mudar formato  
**Recomendação:** Usar biblioteca OCR (pytesseract) ou PDF extractor mais robusto (pdfminer.six)  
**Custo:** 2-3 dias de desenvolvimento

---

### 2. **Sem Cache em Memória** 🟠 ALTO
- ❌ Toda consulta de vendas vai ao banco
- ❌ Sem Redis/Memcached configurado
- ❌ Performance pode degradar com muitos usuários

**Impacto:** Médio - Afeta latência em picos  
**Recomendação:** Adicionar Redis com TTL de 5-15 min em queries frequentes  
**Custo:** 1 dia + $10-20/mês no AWS

---

### 3. **Sem Rate Limiting** 🟠 ALTO
- ❌ DDoS não é protegido
- ❌ Usuários podem fazer 1000s de requisições/sec
- ❌ Sem quota por usuário

**Impacto:** Alto - Segurança da aplicação  
**Recomendação:** Adicionar middleware com sliding window rate limit  
**Custo:** 1 dia de desenvolvimento

---

### 4. **Migrações Alembic Não Testadas** 🟡 MÉDIO
- ❌ Alembic configurado mas sem migrations criadas
- ❌ Sem testes de up/down migration
- ❌ Sem validação de schema em CI

**Impacto:** Médio - Pode quebrar banco em deployment  
**Recomendação:** Gerar migrations, testar em staging antes de prod  
**Custo:** 1 dia

---

### 5. **Sem Observabilidade Centralizada** 🟡 MÉDIO
- ❌ Logs vão apenas para stdout (Docker)
- ❌ Sem CloudWatch Logs agregado
- ❌ Sem métricas de aplicação (CPU, memória)
- ❌ Sem alertas configurados

**Impacto:** Médio - Difícil debugar em produção  
**Recomendação:** Integrar CloudWatch, set up CloudWatch Alarms  
**Custo:** 1-2 dias + $10/mês

---

### 6. **JWT Sem Refresh Token** 🟡 MÉDIO
- ❌ Token expira em 8h sem renovação
- ❌ Usuário precisa fazer login novamente
- ❌ Sem mecanismo de token rotation

**Impacto:** Médio - UX ruim em sessões longas  
**Recomendação:** Implementar refresh token com rotating strategy  
**Custo:** 2 dias

---

### 7. **Sem CORS Configurado** 🟡 MÉDIO
- ❌ Front-end não pode fazer requisições from domains diferentes
- ❌ Sem controle de origins permitidos
- ❌ Sem credentials handling

**Impacto:** Médio - Bloqueia frontend consumir API  
**Recomendação:** Adicionar CORSMiddleware com allowlist de origins  
**Custo:** 2-4 horas

---

### 8. **Testes de Employee Costs Incompletos** 🟡 MÉDIO
- ❌ Testes apenas com mock de PDF
- ❌ Sem testes com PDFs reais
- ❌ Sem testes de edge cases

**Impacto:** Médio - Pode quebrar em produção com PDFs diferentes  
**Recomendação:** Adicionar testes com PDFs reais de diferentes fornecedores  
**Custo:** 2-3 dias

---

### 9. **Sem Validação de Business Rules** 🟡 MÉDIO
- ❌ Quantidade vendida pode ser negativa
- ❌ Preço pode ser zero
- ❌ Sem validação de datas futuras

**Impacto:** Médio - Dados inválidos podem ser persistidos  
**Recomendação:** Adicionar validadores Pydantic customizados  
**Custo:** 1 dia

---

### 10. **CD Não Automatizado** 🟡 MÉDIO
- ❌ CI roda testes, mas não faz deploy
- ❌ Deploy manual via SSH
- ❌ Sem blue-green deployment

**Impacto:** Médio - Deploy lento, erro prone  
**Recomendação:** Adicionar CD ao GitHub Actions (build, push ECR, deploy ECS)  
**Custo:** 2-3 dias

---

## 📊 Matrix de Scores

| Aspecto | Score | Crítico? |
|---------|:-----:|:--------:|
| **Segurança** | 8/10 | 🟠 |
| **Arquitetura** | 8/10 | 🟢 |
| **Qualidade** | 8/10 | 🟢 |
| **Escalabilidade** | 8/10 | 🟡 |
| **Observabilidade** | 7/10 | 🟡 |
| **DevOps** | 8/10 | 🟡 |
| **Robustez Dados** | 8/10 | 🟠 |
| **Documentação** | 7/10 | 🟢 |
| **MÉDIA** | **7.75/10** | - |

---

## 🎯 Recomendações Prioritizadas

### Curto Prazo (Antes de Produção)
1. ✅ **FEITO:** Remover redundâncias de código
2. ⚠️ **TODO:** Adicionar rate limiting middleware
3. ⚠️ **TODO:** Adicionar CORS middleware
4. ⚠️ **TODO:** Testar migrações Alembic

**Tempo Estimado:** 2-3 dias

---

### Médio Prazo (Primeiras 2-4 semanas)
5. ⚠️ **TODO:** Integrar CloudWatch Logs + Alarms
6. ⚠️ **TODO:** Implementar refresh token
7. ⚠️ **TODO:** Melhorar extração de PDF (usar OCR)
8. ⚠️ **TODO:** Adicionar validadores de business rules

**Tempo Estimado:** 3-5 dias

---

### Longo Prazo (Roadmap)
9. ⚠️ **TODO:** Adicionar Redis cache
10. ⚠️ **TODO:** Automatizar CD (GitHub Actions → ECR → EC2)
11. ⚠️ **TODO:** Cobertura de testes 100%
12. ⚠️ **TODO:** APM + Distributed Tracing

**Tempo Estimado:** 1-2 sprints

---

## 🏁 Conclusão

O projeto está em nível **Sênior+ com oportunidades de melhoria**:

- ✅ Fundação sólida: SOLID, async, segurança JWT, testes
- ⚠️ Lacunas: PDF fragile, sem cache, sem rate limit
- 🎯 Pronto para **MVP em produção**, mas precisa de hardening antes de escalar

**Recomendação:** Deploy agora com monitoramento intenso, implementar melhorias conforme feedback de produção.

