# Contrato 06 — Músicas (Navegar R2)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `06-musicas-browse` |
| **Método** | `GET` |
| **Path** | `/api/v1/musicas/browse/` |
| **Status** | Implementado |

## Descrição

Retorna a biblioteca de músicas do R2 com:

- **`tree`** — árvore de pastas e subpastas
- **`musicas`** — mídias da pasta atual (lista)
- **`musicas_list`** — todas as mídias em lista plana (identificação/busca)

Suporta arquivos **`.mp3`** (áudio) e **`.mp4`** (videoclipe).

Raiz padrão: `jukebox/Musicas/` (configurável via `music_root_prefix` no bucket).

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Query params

| Param | Tipo | Descrição |
|---|---|---|
| `prefix` | `string` | Pasta atual (ex: `jukebox/Musicas/Rock/`). Omitir para raiz |
| `bucket_id` | `integer` | ID do bucket. Padrão: bucket `jukebox` ativo |

## Response — Sucesso (`200 OK`)

```json
{
  "bucket_id": 1,
  "bucket_name": "jukebox",
  "root_path": "jukebox/Musicas/",
  "current_path": "jukebox/Musicas/",
  "parent_path": null,
  "tree": {
    "name": "Musicas",
    "path": "jukebox/Musicas/",
    "children": [
      {
        "name": "Rock",
        "path": "jukebox/Musicas/Rock/",
        "children": []
      }
    ]
  },
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
      "folder_path": "jukebox/Musicas/",
      "extension": ".mp3",
      "media_type": "audio",
      "media_url": "https://pub-xxxxx.r2.dev/jukebox/Musicas/song.mp3",
      "audio_url": "https://pub-xxxxx.r2.dev/jukebox/Musicas/song.mp3",
      "size": 5242880,
      "last_modified": "2026-09-01T18:00:00+00:00"
    },
    {
      "name": "clip.mp4",
      "title": "clip",
      "key": "jukebox/Musicas/clip.mp4",
      "folder_path": "jukebox/Musicas/",
      "extension": ".mp4",
      "media_type": "video",
      "media_url": "https://pub-xxxxx.r2.dev/jukebox/Musicas/clip.mp4",
      "audio_url": "https://pub-xxxxx.r2.dev/jukebox/Musicas/clip.mp4",
      "size": 15728640,
      "last_modified": "2026-09-01T18:00:00+00:00"
    }
  ],
  "musicas_list": [],
  "totals": {
    "folders": 3,
    "musicas": 25,
    "audio": 20,
    "video": 5
  }
}
```

### Campos principais

| Campo | Uso no frontend |
|---|---|
| `tree` | Componente de árvore (sidebar) |
| `folders` | Pastas do nível atual |
| `musicas` | Lista da pasta selecionada |
| `musicas_list` | Lista completa para busca/identificação |
| `media_type` | `audio` (mp3) ou `video` (mp4) |
| `media_url` | URL para player (`<audio>` ou `<video>`) |

## Tipos de mídia

| Extensão | `media_type` | Player |
|---|---|---|
| `.mp3` | `audio` | `<audio src={media_url} />` |
| `.mp4` | `video` | `<video src={media_url} />` |
| `.wav`, `.ogg`, `.m4a`, `.flac` | `audio` | `<audio>` |

## Navegação no frontend

1. **Carregar tudo:** `GET /api/v1/musicas/browse/`
2. **Renderizar tree** com `response.tree`
3. **Ao clicar em pasta:** `GET /api/v1/musicas/browse/?prefix={path}`
4. **Listar músicas da pasta:** usar `response.musicas`
5. **Busca global:** filtrar `response.musicas_list` no frontend

## Exemplo

```bash
curl "https://backendjukebox-dev.up.railway.app/api/v1/musicas/browse/" \
  -H "Authorization: Token <token>"
```

## Configuração no bucket

| Campo | Valor |
|---|---|
| `bucket_name` | `jukebox` |
| `music_root_prefix` | `jukebox/Musicas/` |
| `public_base_url` | `https://pub-xxxxx.r2.dev` |

---

## Endpoint legado — CRUD no banco (`GET /api/v1/musicas/`)

Lista músicas cadastradas no PostgreSQL. Para arquivos do R2, use `/browse/`.
