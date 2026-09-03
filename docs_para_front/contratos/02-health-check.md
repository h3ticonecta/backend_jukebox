# Contrato 02 — Health Check

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `02-health-check` |
| **Método** | `GET` |
| **Path** | `/health/` |
| **Versão** | Sem versionamento |
| **Status** | Implementado |

## Descrição

Endpoint de verificação de saúde do serviço. Indica se o backend está operacional. Recomendado para monitoramento e checagem periódica pelo frontend.

## Autenticação

Não requerida.

## Request

### Headers

| Header | Obrigatório | Valor |
|---|---|---|
| `Accept` | Não | `application/json` |

### Query params

Nenhum.

### Body

Nenhum.

## Response — Sucesso (`200 OK`)

### Schema

```json
{
  "status": "string"
}
```

### Campos

| Campo | Tipo | Descrição |
|---|---|---|
| `status` | `string` | Estado de saúde. Valor fixo: `"ok"` |

### Exemplo

```json
{
  "status": "ok"
}
```

## Response — Erros

| Código | Quando |
|---|---|
| `404` | Path incorreto |
| `500` | Erro interno do servidor |
| `502` / `503` | Serviço indisponível (infraestrutura Railway) |

## Exemplos

### cURL

```bash
curl -X GET https://backendjukebox-dev.up.railway.app/health/
```

### TypeScript

```typescript
interface HealthCheckResponse {
  status: string;
}

async function checkHealth(baseUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${baseUrl}/health/`);
    if (!response.ok) return false;

    const data: HealthCheckResponse = await response.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}
```

## Notas para o frontend

- Polling sugerido: a cada 30–60 segundos em telas que dependem do backend.
- Se `status !== "ok"` ou request falhar, exibir estado offline ao usuário.
- Este endpoint **não valida** banco de dados ou serviços externos (R2, etc.) — apenas confirma que o Django está respondendo.
- Futuramente pode ser expandido para incluir checks de dependências:

```json
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "storage": "ok"
  }
}
```

> Formato acima é planejado, **não implementado**.
