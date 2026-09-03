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
| 09 | `CRUD` | `/api/v1/maquinas/` | [09-maquinas.md](./09-maquinas.md) | Implementado |
| 10 | `POST/GET` | `/api/v1/maquinas/creditos/` | [10-maquinas-eventos.md](./10-maquinas-eventos.md) | Implementado |

> Contratos 07 e 08 (CRUD/upload legado) não estão neste pacote — use o **06** (file manager).

## Auth da jukebox (`Maquina`)

| Método | Endpoint | Contrato |
|---|---|---|
| `POST` | `/api/v1/maquinas/auth/` | [09-maquinas.md](./09-maquinas.md) |
| `GET` | `/api/v1/musicas/` | [06-musicas-listar.md](./06-musicas-listar.md) — header `Authorization: Maquina <token>` |
| `POST` | `/api/v1/maquinas/creditos/` | [10-maquinas-eventos.md](./10-maquinas-eventos.md) |
| `POST` | `/api/v1/maquinas/tocadas/` | [10-maquinas-eventos.md](./10-maquinas-eventos.md) |

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
