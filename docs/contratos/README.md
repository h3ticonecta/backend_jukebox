# Contratos de API

Índice dos endpoints implementados e disponíveis para integração.

## Endpoints públicos

| ID | Método | Endpoint | Contrato | Status |
|---|---|---|---|---|
| 01 | `GET` | `/` | [01-service-info.md](./01-service-info.md) | Implementado |
| 02 | `GET` | `/health/` | [02-health-check.md](./02-health-check.md) | Implementado |

## Endpoints autenticados (Token)

| ID | Método | Endpoint | Contrato | Status |
|---|---|---|---|---|
| 03 | `POST` | `/api/v1/auth/token/` | [03-auth-token.md](./03-auth-token.md) | Implementado |
| 04 | `CRUD` | `/api/v1/buckets/` | [04-buckets-crud.md](./04-buckets-crud.md) | Implementado |
| 05 | `Vários` | `/api/v1/buckets/{id}/objects/` | [05-bucket-objects.md](./05-bucket-objects.md) | Implementado |

## Endpoints internos (não para frontend)

| Método | Endpoint | Descrição |
|---|---|---|
| `GET/POST` | `/admin/` | Django Admin (HTML, sessão) |

## Template de contrato

Novos endpoints seguirão esta estrutura:

1. Identificação (método, path, versão)
2. Autenticação
3. Request (headers, params, body)
4. Response (sucesso e erros)
5. Exemplos (curl + JSON)
6. Notas para o frontend
