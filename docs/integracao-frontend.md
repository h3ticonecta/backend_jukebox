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
| [Auth Token](./contratos/03-auth-token.md) | `POST /api/v1/auth/token/` | Obter token de autenticação |
| [Buckets CRUD](./contratos/04-buckets-crud.md) | `/api/v1/buckets/` | Cadastrar conexões S3/R2 |
| [Bucket Objects](./contratos/05-bucket-objects.md) | `/api/v1/buckets/{id}/objects/` | Gerenciar arquivos no bucket |
| [Músicas File Manager](./contratos/06-musicas-listar.md) | `GET /api/v1/musicas/` | Navegar biblioteca (admin ou token da máquina); upload/move/delete só admin |
| [Máquinas](./contratos/09-maquinas.md) | `/api/v1/maquinas/` | Cadastrar jukebox e vincular com usuário/senha |
| [Eventos e relatórios](./contratos/10-maquinas-eventos.md) | `/api/v1/maquinas/creditos/` | Créditos, músicas tocadas, faturamento e ranking |

## 3. Fluxo de autenticação

```typescript
// auth.ts
export async function getApiToken(username: string, password: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) throw new Error('Falha na autenticação');

  const data = await response.json();
  return data.token;
}
```

## 4. Exemplo de integração

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

## 5. O que **não** implementar no frontend agora

| Item | Motivo |
|---|---|
| Login via `/admin/` | É interface HTML do Django, não API |
| Fila de reprodução | Endpoint ainda não existe |
| Votação de músicas | Endpoint ainda não existe |

Consulte o [Roadmap](./roadmap.md) para funcionalidades futuras.

## 6. CORS

Configure no backend a variável:

```
CORS_ALLOWED_ORIGINS=https://seu-frontend.up.railway.app,http://localhost:5173
```

## 7. Checklist de integração

- [ ] Configurar `API_BASE_URL` no `.env` do frontend
- [ ] Implementar health check na inicialização do app
- [ ] Implementar autenticação via token (`/api/v1/auth/token/`)
- [ ] Implementar gestão de buckets conforme contratos 04 e 05
- [ ] Tratar erros de rede (API offline)

## 8. Testar manualmente

```bash
# Obter token
curl -X POST https://backendjukebox-dev.up.railway.app/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua-senha"}'

# Listar buckets
curl https://backendjukebox-dev.up.railway.app/api/v1/buckets/ \
  -H "Authorization: Token <token>"

# Health check
curl https://backendjukebox-dev.up.railway.app/health/
```

Respostas esperadas estão nos contratos individuais.
