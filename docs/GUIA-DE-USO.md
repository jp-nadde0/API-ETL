# Guia Simplificado de Uso

## Requisitos

- Python 3.12 ou superior
- `pip`
- `venv`
- Docker, se quiser subir o fluxo completo em containers

## Uso local

1. Crie e ative o ambiente virtual.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Rode a API com `uvicorn api.api:app --reload --host 0.0.0.0 --port 8000`.

Se quiser o fluxo completo localmente, suba também os containers em `infra/docker/docker-compose.yml`.

## Acesso à API

Você pode usar:

- Swagger UI em `http://localhost:8000/docs`
- Postman, chamando os mesmos endpoints manualmente

## Login

Use as credenciais padrão de desenvolvimento, se elas não tiverem sido alteradas por variáveis de ambiente:

- usuário: `admin`
- senha: `admin123`

O login retorna um JWT. Depois disso, envie o token no header `Authorization: Bearer <token>`.

## Endpoints disponíveis

- `GET /health` - verifica se a API está online
- `POST /auth/login` - gera o token
- `POST /extract_produtos/` - lê planilha XLSX de vendas
- `POST /resumir_vendas/` - resume as vendas da planilha
- `POST /vendas/persistir/` - extrai e grava as vendas no banco
- `POST /extract_employee_costs/` - lê o PDF de folha e grava no DynamoDB

## Arquivos para teste

Use os arquivos que já estão na pasta `files/`:

- `files/sales_worksheet.xlsx` para testes de vendas
- `files/payroll.pdf` para testes de custos de funcionários

## Produção

Se quiser testar sem subir nada localmente, a API já está atrás do Nginx em:

`http://44.203.108.22`

Você pode abrir:

- `http://44.203.108.22/docs`
- `http://44.203.108.22/openapi.json`

## Sequência mínima de uso

1. Faça login em `POST /auth/login`.
2. Copie o token.
3. Envie o arquivo desejado em um dos endpoints protegidos.
4. Para vendas, use o XLSX.
5. Para custos de funcionários, use o PDF.