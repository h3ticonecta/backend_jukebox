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
| 06 | `GET` | `/api/v1/musicas/` | [06-musicas-listar.md](./06-musicas-listar.md) | Implementado |
| 07 | `CRUD` | `/api/v1/musicas/` | [07-musicas-crud.md](./07-musicas-crud.md) | Implementado |
| 08 | `POST` | `/api/v1/musicas/{id}/upload/` | [08-musicas-upload.md](./08-musicas-upload.md) | Implementado |
| 09 | `CRUD` | `/api/v1/maquinas/` | [09-maquinas.md](./09-maquinas.md) | Implementado |
| 10 | `POST/GET` | `/api/v1/maquinas/creditos/` | [10-maquinas-eventos.md](./10-maquinas-eventos.md) | Implementado |

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
