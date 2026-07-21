# Arquitetura do Projeto

## Visão geral

O projeto tem três partes principais:

- Backend em FastAPI
- Persistência em PostgreSQL e DynamoDB
- Infraestrutura na AWS com EC2, Nginx, Terraform e Docker

## Backend

O backend fica em `api/` e concentra a API, autenticação, tratamento de erros, logging e serviços de negócio.

- A execução em produção usa Python 3.12 nos containers Docker
- `api/api.py` expõe os endpoints
- `api/auth.py` gera e valida JWT
- `api/exceptions.py` padroniza os erros
- `api/services/` faz a orquestração das regras de negócio
- `extractors/` trata a leitura de XLSX e PDF
- `database/repositories/` faz o acesso aos dados

Fluxo básico:

1. O cliente envia o arquivo para a API.
2. A API valida o token e o formato do arquivo.
3. O extractor processa os dados.
4. O serviço persiste o resultado.
5. A resposta volta em JSON.

## Autenticação

O acesso aos endpoints protegidos usa JWT.

- Login em `POST /auth/login`
- O token é enviado no header `Authorization: Bearer <token>`
- O token expira em 8 horas

## Banco de dados

O projeto usa dois armazenamentos, cada um para um tipo de dado:

- PostgreSQL: dados de vendas e consultas relacionais
- DynamoDB: custos de funcionários extraídos do PDF

O PostgreSQL é acessado pela API por meio do `DATABASE_URL`. O DynamoDB é usado pelo repositório de custos de funcionários.

## Infraestrutura

A infraestrutura é provisionada com Terraform e roda na AWS.

- EC2 hospeda os containers e o Nginx
- Nginx faz reverse proxy para a API interna em `127.0.0.1:8000`
- A API e o extractor rodam em containers Docker
- O RDS PostgreSQL fica em subnet privada
- A VPC inclui subnets públicas e privadas, internet gateway e security groups
- O projeto usa um endpoint de VPC para acesso ao DynamoDB

## Rede

Em produção, a porta pública é a do Nginx.

- Nginx escuta em `80`
- A API fica atrás do proxy, sem exposição direta para o usuário final
- O IP público atual da EC2/Nginx é `44.203.108.22`

## Estrutura de acesso

- Swagger UI: `/docs`
- OpenAPI: `/openapi.json`
- Health check: `/health`

## Arquivos de teste

Os arquivos para testar a aplicação ficam na pasta `files/`:

- `files/sales_worksheet.xlsx`
- `files/payroll.pdf`