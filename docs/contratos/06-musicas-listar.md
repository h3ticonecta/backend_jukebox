# Contrato 06 — Músicas (Listar e Detalhar)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `06-musicas-listar` |
| **Base path** | `/api/v1/musicas/` |
| **Status** | Implementado |

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/v1/musicas/` | Listar músicas |
| `GET` | `/api/v1/musicas/{id}/` | Detalhar música |

## Query params (listagem)

| Param | Tipo | Descrição |
|---|---|---|
| `artist` | `string` | Filtrar por artista (parcial) |
| `album` | `string` | Filtrar por álbum (parcial) |
| `is_active` | `boolean` | Filtrar por status (`true`/`false`) |

## Response — Sucesso (`200 OK`)

```json
{
  "id": 1,
  "title": "Nome da Música",
  "artist": "Artista",
  "album": "Álbum",
  "storage_key": "musicas/1/song.mp3",
  "audio_url": "https://pub-xxxxx.r2.dev/musicas/1/song.mp3",
  "duration_seconds": 180,
  "file_size": 5242880,
  "content_type": "audio/mpeg",
  "bucket_id": 1,
  "bucket_name": "jukebox-prod",
  "is_active": true,
  "created_at": "2026-09-01T20:00:00Z",
  "updated_at": "2026-09-01T20:00:00Z"
}
```

> `audio_url` é `null` se o bucket não tiver `public_base_url` ou se a música não tiver arquivo.

## Notas para o frontend

- Usar `audio_url` diretamente no player: `<audio src={musica.audio_url} />`
- Listagem retorna array paginado pelo DRF (formato padrão com `count`, `next`, `previous`, `results`)
