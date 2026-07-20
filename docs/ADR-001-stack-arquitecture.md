# ADR-001: Stack Escolhida

**Data:** 2026-07-20  
**Status:** Aceito

## Decisão

A aplicação usa esta stack:

- Backend: FastAPI
- Autenticação: JWT com Bearer token
- Banco relacional: PostgreSQL
- Banco NoSQL: DynamoDB para os custos de funcionários
- Infraestrutura: Docker, Terraform, EC2 e Nginx
- Testes: pytest

## Motivo

Essa combinação foi escolhida para manter a API simples de manter, com documentação automática, autenticação stateless e implantação direta na AWS.

## Resultado

O backend expõe a API em FastAPI, o Nginx fica na borda da instância EC2 e a persistência fica dividida entre PostgreSQL e DynamoDB conforme o tipo de dado.

