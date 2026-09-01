# Contratos de API

Índice dos endpoints implementados e disponíveis para integração.

## Endpoints públicos

| ID | Método | Endpoint | Contrato | Status |
|---|---|---|---|---|
| 01 | `GET` | `/` | [01-service-info.md](./01-service-info.md) | Implementado |
| 02 | `GET` | `/health/` | [02-health-check.md](./02-health-check.md) | Implementado |

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
