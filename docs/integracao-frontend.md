# Integração Frontend

Guia prático para o time de frontend integrar com o backend atual.

## 1. Configurar base URL

```typescript
// Exemplo (TypeScript)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  ?? 'https://backendjukebox-dev.up.railway.app';
```

## 2. Endpoints disponíveis hoje

| Contrato | Endpoint | Uso sugerido no frontend |
|---|---|---|
| [Service Info](./contratos/01-service-info.md) | `GET /` | Verificar se a API está no ar |
| [Health Check](./contratos/02-health-check.md) | `GET /health/` | Monitoramento / status page |

## 3. Exemplo de integração

```typescript
// health.ts
export async function checkApiHealth(): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/health/`);
  if (!response.ok) return false;

  const data = await response.json();
  return data.status === 'ok';
}
```

```typescript
// service-info.ts
type ServiceInfo = {
  service: string;
  status: string;
  endpoints: {
    health: string;
    admin: string;
  };
};

export async function getServiceInfo(): Promise<ServiceInfo> {
  const response = await fetch(`${API_BASE_URL}/`);
  if (!response.ok) {
    throw new Error('API indisponível');
  }
  return response.json();
}
```

## 4. O que **não** implementar no frontend agora

| Item | Motivo |
|---|---|
| Login via `/admin/` | É interface HTML do Django, não API |
| Upload de músicas | Endpoint ainda não existe |
| Fila de reprodução | Endpoint ainda não existe |
| Votação de músicas | Endpoint ainda não existe |

Consulte o [Roadmap](./roadmap.md) para funcionalidades futuras.

## 5. CORS

Antes de integrar em produção, informe ao backend:

- URL do frontend no Railway (ex: `https://frontend-jukebox-dev.up.railway.app`)

O backend configurará `CORS_ALLOWED_ORIGINS` para permitir requisições cross-origin.

## 6. Checklist de integração

- [ ] Configurar `API_BASE_URL` no `.env` do frontend
- [ ] Implementar health check na inicialização do app
- [ ] Tratar erros de rede (API offline)
- [ ] Aguardar contratos de autenticação antes de implementar login
- [ ] Aguardar contratos de músicas/fila antes de implementar player

## 7. Testar manualmente

```bash
# Health check
curl https://backendjukebox-dev.up.railway.app/health/

# Service info
curl https://backendjukebox-dev.up.railway.app/
```

Respostas esperadas estão nos contratos individuais.
