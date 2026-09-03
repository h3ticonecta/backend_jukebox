# Contrato 04 — Buckets (CRUD)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `04-buckets-crud` |
| **Base path** | `/api/v1/buckets/` |
| **Status** | Implementado |

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/v1/buckets/` | Listar configurações |
| `POST` | `/api/v1/buckets/` | Criar configuração |
| `GET` | `/api/v1/buckets/{id}/` | Detalhar configuração |
| `PUT` | `/api/v1/buckets/{id}/` | Atualizar configuração |
| `PATCH` | `/api/v1/buckets/{id}/` | Atualizar parcialmente |
| `DELETE` | `/api/v1/buckets/{id}/` | Remover configuração |
| `POST` | `/api/v1/buckets/{id}/test-connection/` | Testar conexão |

## Schema — Bucket (leitura)

```json
{
  "id": 1,
  "name": "musica-prod",
  "provider": "cloudflare_r2",
  "provider_display": "Cloudflare R2",
  "endpoint_url": "https://<account_id>.r2.cloudflarestorage.com",
  "public_base_url": "https://pub-xxxxx.r2.dev",
  "music_root_prefix": "jukebox/Musicas/",
  "bucket_name": "jukebox-musicas",
  "access_key_id": "ACCESS_KEY",
  "region_name": "auto",
  "is_active": true,
  "created_at": "2026-09-01T20:00:00Z",
  "updated_at": "2026-09-01T20:00:00Z"
}
```

> `secret_access_key` **nunca** é retornada nas respostas de leitura.

## Schema — Criar bucket (`POST`)

```json
{
  "name": "musica-prod",
  "provider": "cloudflare_r2",
  "endpoint_url": "https://<account_id>.r2.cloudflarestorage.com",
  "public_base_url": "https://pub-xxxxx.r2.dev",
  "music_root_prefix": "jukebox/Musicas/",
  "bucket_name": "jukebox-musicas",
  "access_key_id": "ACCESS_KEY",
  "secret_access_key": "SECRET_KEY",
  "region_name": "auto",
  "is_active": true
}
```

### Provedores aceitos

| Valor | Descrição |
|---|---|
| `cloudflare_r2` | Cloudflare R2 |
| `aws_s3` | AWS S3 |

## Schema — Atualizar bucket (`PUT` / `PATCH`)

Mesmos campos da criação. `secret_access_key` é opcional — se omitida, mantém a atual.

## Testar conexão (`POST /api/v1/buckets/{id}/test-connection/`)

### Response — Sucesso

```json
{
  "bucket_id": 1,
  "bucket_name": "jukebox-musicas",
  "connected": true,
  "bucket": "jukebox-musicas"
}
```

## Exemplo — Criar bucket R2

```bash
curl -X POST https://backendjukebox-dev.up.railway.app/api/v1/buckets/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "musica-prod",
    "provider": "cloudflare_r2",
    "endpoint_url": "https://ACCOUNT_ID.r2.cloudflarestorage.com",
    "bucket_name": "jukebox-musicas",
    "access_key_id": "SUA_ACCESS_KEY",
    "secret_access_key": "SUA_SECRET_KEY",
    "region_name": "auto"
  }'
```

## Notas para o frontend

- Cadastrar buckets via API ou Django Admin (`/admin/`)
- Sempre testar conexão após criar/editar credenciais
- Um bucket inativo (`is_active: false`) não permite operações de arquivos
