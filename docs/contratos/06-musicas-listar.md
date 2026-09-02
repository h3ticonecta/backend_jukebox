# Contrato 06 — Músicas (Navegar R2)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `06-musicas-browse` |
| **Método** | `GET` |
| **Path** | `/api/v1/musicas/browse/` |
| **Status** | Implementado |

## Descrição

Lista **pastas e músicas diretamente do R2**, navegando pela estrutura do bucket. Endpoint principal para a aba de músicas no frontend.

Por padrão, inicia em `jukebox/Musicas/` (configurável no bucket via `music_root_prefix`).

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Query params

| Param | Tipo | Descrição |
|---|---|---|
| `prefix` | `string` | Pasta atual (ex: `jukebox/Musicas/Rock/`). Omitir para raiz das músicas |
| `bucket_id` | `integer` | ID do bucket. Padrão: bucket `jukebox` ativo |
| `max_keys` | `integer` | Máximo de itens (padrão: 100, máx: 1000) |
| `continuation_token` | `string` | Paginação S3 |

## Response — Sucesso (`200 OK`)

```json
{
  "bucket_id": 1,
  "bucket_name": "jukebox",
  "root_path": "jukebox/Musicas/",
  "current_path": "jukebox/Musicas/",
  "parent_path": null,
  "folders": [
    {
      "name": "Rock",
      "path": "jukebox/Musicas/Rock/"
    }
  ],
  "musicas": [
    {
      "name": "song.mp3",
      "title": "song",
      "key": "jukebox/Musicas/song.mp3",
      "audio_url": "https://pub-xxxxx.r2.dev/jukebox/Musicas/song.mp3",
      "size": 5242880,
      "last_modified": "2026-09-01T18:00:00+00:00"
    }
  ],
  "is_truncated": false,
  "next_continuation_token": null
}
```

### Campos

| Campo | Descrição |
|---|---|
| `root_path` | Pasta raiz das músicas no bucket |
| `current_path` | Pasta sendo exibida |
| `parent_path` | Pasta pai (`null` na raiz) |
| `folders` | Subpastas para navegação |
| `musicas` | Arquivos de áudio da pasta atual (`.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`) |

## Navegação no frontend

1. **Carregar raiz:** `GET /api/v1/musicas/browse/`
2. **Entrar em pasta:** `GET /api/v1/musicas/browse/?prefix=jukebox/Musicas/Rock/`
3. **Voltar:** usar `parent_path` da resposta anterior
4. **Tocar música:** usar `audio_url` do item em `musicas`

## Exemplo

```bash
# Raiz das músicas
curl "https://backendjukebox-dev.up.railway.app/api/v1/musicas/browse/" \
  -H "Authorization: Token <token>"

# Subpasta
curl "https://backendjukebox-dev.up.railway.app/api/v1/musicas/browse/?prefix=jukebox/Musicas/Rock/" \
  -H "Authorization: Token <token>"
```

## Configuração no bucket

No cadastro do bucket (`/api/v1/buckets/` ou Admin), configure:

| Campo | Valor |
|---|---|
| `bucket_name` | `jukebox` |
| `music_root_prefix` | `jukebox/Musicas/` |
| `public_base_url` | `https://pub-xxxxx.r2.dev` |

---

## Endpoint legado — CRUD no banco (`GET /api/v1/musicas/`)

Lista músicas cadastradas no PostgreSQL (metadados). Para listar arquivos do R2, use `/browse/`.
