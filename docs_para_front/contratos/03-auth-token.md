# Contrato 03 — Autenticação (Token)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `03-auth-token` |
| **Método** | `POST` |
| **Path** | `/api/v1/auth/token/` |
| **Status** | Implementado |

## Descrição

Obtém token de autenticação para consumir os endpoints protegidos da API (buckets).

## Autenticação

Não requerida neste endpoint.

## Request

### Headers

| Header | Valor |
|---|---|
| `Content-Type` | `application/json` |

### Body

```json
{
  "username": "admin",
  "password": "sua-senha"
}
```

## Response — Sucesso (`200 OK`)

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

## Response — Erros

| Código | Quando |
|---|---|
| `400` | Credenciais ausentes ou inválidas |

## Uso nos demais endpoints

```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Exemplo

```bash
curl -X POST https://backendjukebox-dev.up.railway.app/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua-senha"}'
```
