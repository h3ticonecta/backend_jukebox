# Convenções de API

Padrões adotados pelo backend e que o frontend deve seguir na integração.

## Formato

| Item | Padrão |
|---|---|
| Protocolo | HTTPS (produção) / HTTP (local) |
| Formato de dados | JSON (`Content-Type: application/json`) |
| Encoding | UTF-8 |
| Idioma das mensagens | Português (pt-BR) quando aplicável |
| Fuso horário do servidor | `America/Sao_Paulo` |

## Métodos HTTP

| Método | Uso |
|---|---|
| `GET` | Consulta de dados |
| `POST` | Criação de recursos |
| `PUT` / `PATCH` | Atualização de recursos |
| `DELETE` | Remoção de recursos |

## Estrutura de resposta (sucesso)

Endpoints atuais retornam JSON direto, sem envelope:

```json
{
  "campo": "valor"
}
```

> Endpoints futuros podem adotar envelope padronizado. Será documentado nos respectivos contratos.

## Estrutura de erro (padrão futuro)

Quando a API REST for implementada, erros seguirão este formato:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Descrição legível do erro",
    "details": {}
  }
}
```

## Códigos HTTP

| Código | Significado |
|---|---|
| `200` | Sucesso |
| `201` | Recurso criado |
| `400` | Requisição inválida |
| `401` | Não autenticado |
| `403` | Sem permissão |
| `404` | Recurso não encontrado |
| `500` | Erro interno do servidor |

## Autenticação (status atual)

| Contexto | Mecanismo | Status |
|---|---|---|
| Endpoints públicos (`/`, `/health/`) | Nenhum | Implementado |
| Django Admin (`/admin/`) | Sessão + CSRF (cookie) | Implementado |
| API para frontend | Token (`Authorization: Token <token>`) | Implementado |

Obter token: `POST /api/v1/auth/token/`

## CORS (status atual)

Configurado via variável de ambiente:

```
CORS_ALLOWED_ORIGINS=https://<dominio-do-frontend>,http://localhost:5173
```

## Versionamento (planejado)

Endpoints futuros poderão usar prefixo de versão:

```
/api/v1/musicas/
```

Endpoints atuais (`/`, `/health/`) não possuem versionamento.

## Headers recomendados (frontend)

```http
Accept: application/json
Content-Type: application/json
```

Para endpoints autenticados (futuro):

```http
Authorization: Bearer <token>
```
