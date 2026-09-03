# Contrato 05 — Objetos do Bucket

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `05-bucket-objects` |
| **Base path** | `/api/v1/buckets/{id}/objects/` |
| **Status** | Implementado |

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/v1/buckets/{id}/objects/` | Listar arquivos |
| `POST` | `/api/v1/buckets/{id}/objects/upload/` | Upload de arquivo |
| `POST` | `/api/v1/buckets/{id}/objects/move/` | Mover arquivo |
| `POST` | `/api/v1/buckets/{id}/objects/delete/` | Excluir arquivos |

---

## 5.1 Listar arquivos

### Request

```
GET /api/v1/buckets/{id}/objects/?prefix=musicas/&max_keys=100&continuation_token=...
```

| Query param | Tipo | Descrição |
|---|---|---|
| `prefix` | `string` | Filtrar por pasta/caminho (opcional) |
| `max_keys` | `integer` | Máximo de itens (padrão: 100, máx: 1000) |
| `continuation_token` | `string` | Paginação S3 (opcional) |

### Response — Sucesso (`200 OK`)

```json
{
  "bucket_id": 1,
  "bucket_name": "jukebox-musicas",
  "prefix": "musicas/",
  "objects": [
    {
      "key": "musicas/song.mp3",
      "size": 5242880,
      "last_modified": "2026-09-01T18:00:00+00:00",
      "etag": "d41d8cd98f00b204e9800998ecf8427e",
      "public_url": "https://pub-xxxxx.r2.dev/musicas/song.mp3"
    }
  ],
  "folders": ["musicas/album1/"],
  "is_truncated": false,
  "next_continuation_token": null,
  "key_count": 1
}
```

---

## 5.2 Upload

### Request

```
POST /api/v1/buckets/{id}/objects/upload/
Content-Type: multipart/form-data
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `file` | `file` | Sim | Arquivo a enviar |
| `key` | `string` | Não | Caminho no bucket (padrão: nome do arquivo) |

### Response — Sucesso (`201 Created`)

```json
{
  "bucket_id": 1,
  "key": "musicas/song.mp3",
  "bucket": "jukebox-musicas"
}
```

### Exemplo

```bash
curl -X POST https://backendjukebox-dev.up.railway.app/api/v1/buckets/1/objects/upload/ \
  -H "Authorization: Token <token>" \
  -F "file=@song.mp3" \
  -F "key=musicas/song.mp3"
```

---

## 5.3 Mover arquivo

### Request

```
POST /api/v1/buckets/{id}/objects/move/
Content-Type: application/json
```

```json
{
  "source_key": "musicas/old-name.mp3",
  "destination_key": "musicas/novo-nome.mp3"
}
```

### Response — Sucesso (`200 OK`)

```json
{
  "bucket_id": 1,
  "source_key": "musicas/old-name.mp3",
  "destination_key": "musicas/novo-nome.mp3",
  "bucket": "jukebox-musicas"
}
```

---

## 5.4 Excluir arquivos

### Request

```
POST /api/v1/buckets/{id}/objects/delete/
Content-Type: application/json
```

```json
{
  "keys": [
    "musicas/song1.mp3",
    "musicas/song2.mp3"
  ]
}
```

### Response — Sucesso (`200 OK`)

```json
{
  "bucket_id": 1,
  "deleted": ["musicas/song1.mp3", "musicas/song2.mp3"],
  "errors": [],
  "bucket": "jukebox-musicas"
}
```

---

## Erros comuns

```json
{
  "error": {
    "code": "NoSuchKey",
    "message": "The specified key does not exist."
  }
}
```

| Código HTTP | Quando |
|---|---|
| `400` | Parâmetros inválidos ou erro S3/R2 |
| `401` | Token ausente ou inválido |
| `404` | Bucket não encontrado ou inativo |

## Notas para o frontend

- Use `folders` para navegação tipo explorador de arquivos
- Use `next_continuation_token` para paginar listagens grandes
- Upload deve usar `multipart/form-data`, não JSON
- Mover = copiar + excluir origem (operação atômica no serviço)
