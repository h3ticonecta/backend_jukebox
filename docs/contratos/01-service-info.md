# Contrato 01 — Service Info

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `01-service-info` |
| **Método** | `GET` |
| **Path** | `/` |
| **Versão** | Sem versionamento |
| **Status** | Implementado |

## Descrição

Retorna informações básicas do serviço e lista os endpoints disponíveis. Útil para verificar se a API está respondendo e descobrir rotas.

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
  "service": "string",
  "status": "string",
  "endpoints": {
    "health": "string",
    "admin": "string"
  }
}
```

### Campos

| Campo | Tipo | Descrição |
|---|---|---|
| `service` | `string` | Nome do serviço. Valor fixo: `"backend_jukebox"` |
| `status` | `string` | Estado do serviço. Valor fixo: `"running"` |
| `endpoints.health` | `string` | Path relativo do health check |
| `endpoints.admin` | `string` | Path relativo do Django Admin |

### Exemplo

```json
{
  "service": "backend_jukebox",
  "status": "running",
  "endpoints": {
    "health": "/health/",
    "admin": "/admin/"
  }
}
```

## Response — Erros

| Código | Quando |
|---|---|
| `404` | Path incorreto |
| `500` | Erro interno do servidor |

## Exemplos

### cURL

```bash
curl -X GET https://backendjukebox-dev.up.railway.app/
```

### TypeScript

```typescript
interface ServiceInfoResponse {
  service: string;
  status: string;
  endpoints: {
    health: string;
    admin: string;
  };
}

async function fetchServiceInfo(baseUrl: string): Promise<ServiceInfoResponse> {
  const response = await fetch(`${baseUrl}/`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}
```

## Notas para o frontend

- Usar na inicialização do app para confirmar conectividade com o backend.
- O campo `endpoints.admin` é informativo; o frontend **não deve** integrar com `/admin/`.
- Novos endpoints serão adicionados ao objeto `endpoints` conforme forem implementados.
