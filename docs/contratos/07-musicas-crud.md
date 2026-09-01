# Contrato 07 — Músicas (Criar, Atualizar, Excluir)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `07-musicas-crud` |
| **Base path** | `/api/v1/musicas/` |
| **Status** | Implementado |

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/api/v1/musicas/` | Criar música (metadados) |
| `PUT` | `/api/v1/musicas/{id}/` | Atualizar música |
| `PATCH` | `/api/v1/musicas/{id}/` | Atualizar parcialmente |
| `DELETE` | `/api/v1/musicas/{id}/` | Excluir música e arquivo no R2 |

## Request — Criar (`POST`)

```json
{
  "title": "Nome da Música",
  "artist": "Artista",
  "album": "Álbum",
  "bucket_id": 1,
  "duration_seconds": 180,
  "is_active": true
}
```

### Campos

| Campo | Obrigatório | Descrição |
|---|---|---|
| `title` | Sim | Título da música |
| `artist` | Não | Nome do artista |
| `album` | Não | Nome do álbum |
| `bucket_id` | Sim | ID do `BucketConfig` ativo com `public_base_url` |
| `duration_seconds` | Não | Duração em segundos |
| `is_active` | Não | Padrão: `true` |

### Response — Sucesso (`201 Created`)

Retorna o objeto completo (mesmo schema do contrato 06).

## Excluir (`DELETE`)

Remove a música do banco e tenta excluir o arquivo no R2.

### Response — Sucesso (`204 No Content`)

Sem body.

## Exemplo

```bash
curl -X POST https://backendjukebox-dev.up.railway.app/api/v1/musicas/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Minha Música",
    "artist": "Artista",
    "bucket_id": 1
  }'
```

## Notas para o frontend

- Após criar, fazer upload do arquivo com o [Contrato 08](./08-musicas-upload.md)
- O bucket deve ter `public_base_url` configurada, senão a criação retorna erro de validação
