# Contrato 06 — Músicas (File Manager R2)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `06-musicas-file-manager` |
| **Base path** | `/api/v1/musicas/` |
| **Status** | Implementado |

## Descrição

A aba de músicas funciona como um **gerenciador de arquivos** do R2. Não é necessário cadastrar músicas separadamente — os arquivos são lidos diretamente do bucket na pasta configurada (padrão efetivo: `Musicas/`).

Suporta:
- Áudio: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`
- Vídeo: `.mp4`
- Capa de álbum: `.jpg`, `.jpeg`, `.png`

A capa da pasta é escolhida nesta ordem de nome (sem extensão): `cover`, `folder`, `album`, `artwork`, `front`, `capa`. Se nenhum desses existir, usa a primeira imagem da pasta.

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/v1/musicas/` | Navegar pastas e listar arquivos |
| `GET` | `/api/v1/musicas/browse/` | Alias do endpoint acima |
| `POST` | `/api/v1/musicas/upload/` | Upload na pasta atual |
| `POST` | `/api/v1/musicas/move/` | Mover arquivo |
| `POST` | `/api/v1/musicas/delete/` | Excluir arquivos |
| `POST` | `/api/v1/musicas/folders/` | Criar subpasta |

---

## 1. Navegar (GET)

```
GET /api/v1/musicas/?prefix=jukebox/Musicas/Rock/
```

| Query | Descrição |
|---|---|
| `prefix` | Pasta atual (omitir = raiz `jukebox/Musicas/`) |
| `bucket_id` | Opcional — padrão: bucket `jukebox` |

### Response

```json
{
  "mode": "file_manager",
  "bucket_id": 1,
  "bucket_name": "jukebox",
  "root_path": "Musicas/",
  "current_path": "Musicas/Rock/",
  "parent_path": "Musicas/",
  "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg",
  "cover": {
    "name": "cover.jpg",
    "key": "Musicas/Rock/cover.jpg",
    "media_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg"
  },
  "breadcrumbs": [
    { "name": "Musicas", "path": "Musicas/" },
    { "name": "Rock", "path": "Musicas/Rock/" }
  ],
  "tree": {
    "name": "Musicas",
    "path": "Musicas/",
    "cover_url": null,
    "children": [
      {
        "name": "Rock",
        "path": "Musicas/Rock/",
        "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg",
        "children": []
      }
    ]
  },
  "folders": [
    {
      "name": "Pop",
      "path": "Musicas/Pop/",
      "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Pop/folder.jpg",
      "cover": {
        "name": "folder.jpg",
        "key": "Musicas/Pop/folder.jpg",
        "media_url": "https://pub-xxxxx.r2.dev/Musicas/Pop/folder.jpg"
      }
    }
  ],
  "files": [
    {
      "name": "song.mp3",
      "title": "song",
      "key": "Musicas/Rock/song.mp3",
      "folder_path": "Musicas/Rock/",
      "extension": ".mp3",
      "media_type": "audio",
      "media_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/song.mp3",
      "audio_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/song.mp3",
      "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg",
      "cover": {
        "name": "cover.jpg",
        "key": "Musicas/Rock/cover.jpg",
        "media_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg"
      },
      "size": 5242880,
      "last_modified": "2026-09-01T18:00:00+00:00"
    }
  ],
  "images": [
    {
      "name": "cover.jpg",
      "title": "cover",
      "key": "Musicas/Rock/cover.jpg",
      "folder_path": "Musicas/Rock/",
      "extension": ".jpg",
      "media_type": "image",
      "media_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg",
      "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg",
      "size": 204800,
      "last_modified": "2026-09-01T18:00:00+00:00"
    }
  ],
  "files_list": [],
  "images_list": [],
  "totals": {
    "folders": 5,
    "files": 120,
    "images": 40,
    "audio": 100,
    "video": 20
  }
}
```

### Uso no frontend

| Campo | Componente UI |
|---|---|
| `tree` | Árvore lateral (sidebar); `cover_url` opcional |
| `breadcrumbs` | Barra de navegação |
| `folders` | Ícones/capas de pasta na área principal |
| `files` | Lista de músicas/vídeos da pasta atual (`cover_url` = capa do álbum) |
| `images` | Fotos jpg/png da pasta atual |
| `files_list` | Busca global de faixas em todas as pastas |
| `images_list` | Todas as capas/fotos |
| `cover_url` | Capa da pasta atual |

---

## 2. Upload (POST)

```
POST /api/v1/musicas/upload/
Content-Type: multipart/form-data
```

| Campo | Tipo | Descrição |
|---|---|---|
| `file` | file | Áudio, vídeo ou capa (`.jpg`, `.jpeg`, `.png`) |
| `prefix` | string | Pasta destino (ex: `Musicas/Rock/`) |

---

## 3. Mover (POST)

```json
POST /api/v1/musicas/move/
{
  "source_key": "jukebox/Musicas/old.mp3",
  "destination_key": "jukebox/Musicas/Rock/old.mp3"
}
```

---

## 4. Excluir (POST)

```json
POST /api/v1/musicas/delete/
{
  "keys": ["jukebox/Musicas/Rock/song.mp3"]
}
```

---

## 5. Criar pasta (POST)

```json
POST /api/v1/musicas/folders/
{
  "prefix": "jukebox/Musicas/",
  "name": "Rock"
}
```

---

## Fluxo do frontend (file manager)

```
1. GET /musicas/                    → monta tree + lista raiz
2. Clicar pasta "Rock"              → GET /musicas/?prefix=jukebox/Musicas/Rock/
3. Clicar breadcrumb                → GET /musicas/?prefix={path}
4. Upload                           → POST /musicas/upload/ com prefix atual
5. Tocar arquivo                    → usar file.media_url no player
6. Busca                            → filtrar files_list localmente
```

## Notas

- Não use CRUD separado de músicas — tudo vem do R2
- Configure o bucket no Django Admin (`/admin/`) com `music_root_prefix`
- Campos `musicas` e `musicas_list` mantidos como alias de `files` e `files_list` (somente áudio/vídeo)
- JPG/PNG não entram em `files` para o player não tentar tocá-los; use `images` / `cover_url`
