# Contrato 06 — Músicas (File Manager R2)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `06-musicas-file-manager` |
| **Base path** | `/api/v1/musicas/` |
| **Status** | Implementado |

## Descrição

A aba de músicas funciona como um **gerenciador de arquivos**. O R2 é lido só na **sincronização**; navegação e busca usam o catálogo em cache no PostgreSQL.

Suporta:
- Áudio: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`
- Vídeo: `.mp4`
- Capa de álbum: `.jpg`, `.jpeg`, `.png`

A capa da pasta é escolhida nesta ordem de nome (sem extensão): `cover`, `folder`, `album`, `artwork`, `front`, `capa`. Se nenhum desses existir, usa a primeira imagem da pasta.

Antes do primeiro `POST /sync/`, `needs_sync` vem `true` e as listas ficam vazias.

## Autenticação

| Endpoint | Auth aceita |
|---|---|
| `GET /musicas/` e `GET /musicas/browse/` | Token **admin** (`Authorization: Token <token>`) **ou** token da jukebox (`Authorization: Maquina <token>`) |
| `POST` (sync, upload, move, delete, folders) | Somente token **admin** |

O token da máquina vem de `POST /api/v1/maquinas/auth/` após login com usuário/senha da jukebox.

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/v1/musicas/` | Navegar o catálogo em cache |
| `GET` | `/api/v1/musicas/browse/` | Alias do endpoint acima |
| `POST` | `/api/v1/musicas/sync/` | Relê o R2 e atualiza o PostgreSQL |
| `POST` | `/api/v1/musicas/upload/` | Upload na pasta atual |
| `POST` | `/api/v1/musicas/move/` | Mover arquivo |
| `POST` | `/api/v1/musicas/delete/` | Excluir arquivos |
| `POST` | `/api/v1/musicas/folders/` | Criar subpasta |

---

## 1. Navegar (GET)

```
GET /api/v1/musicas/?prefix=Musicas/Rock/
GET /api/v1/musicas/?q=love
```

| Query | Descrição |
|---|---|
| `prefix` | Pasta atual (omitir = raiz do catálogo) |
| `q` | Busca no catálogo (nome/chave), sem consultar o R2 |
| `bucket_id` | Opcional — padrão: bucket `jukebox` |

### Response

```json
{
  "mode": "file_manager",
  "cached": true,
  "needs_sync": false,
  "is_syncing": false,
  "last_synced_at": "2026-09-02T16:00:00+00:00",
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
| `files` | Lista da pasta atual: áudio, vídeo e imagens (`media_type`) |
| `musicas` | Somente áudio/vídeo da pasta atual (para o player) |
| `images` | Fotos jpg/png da pasta atual |
| `files_list` | Busca global de faixas em todas as pastas |
| `images_list` | Todas as capas/fotos |
| `cover_url` | Capa da pasta atual |
| `cached` / `needs_sync` | Se o catálogo PostgreSQL já foi sincronizado |
| `last_synced_at` | Data da última leitura do R2 |

---

## 2. Sincronizar (POST)

```
POST /api/v1/musicas/sync/
```

Relê o bucket R2 e substitui o catálogo no PostgreSQL. Pode demorar na primeira vez. Enquanto roda, um segundo `POST` retorna `409 SYNC_IN_PROGRESS`.

```json
{
  "bucket_id": 1,
  "synced": true,
  "root_path": "Musicas/",
  "last_synced_at": "2026-09-02T16:00:00+00:00",
  "folders": 40,
  "files": 120,
  "images": 35
}
```

---

## 3. Upload (POST)

```
POST /api/v1/musicas/upload/
Content-Type: multipart/form-data
```

| Campo | Tipo | Descrição |
|---|---|---|
| `file` | file | Áudio, vídeo ou capa (`.jpg`, `.jpeg`, `.png`) |
| `prefix` | string | Pasta destino (ex: `Musicas/Rock/`) |

---

## 4. Mover (POST)

```json
POST /api/v1/musicas/move/
{
  "source_key": "jukebox/Musicas/old.mp3",
  "destination_key": "jukebox/Musicas/Rock/old.mp3"
}
```

---

## 5. Excluir (POST)

```json
POST /api/v1/musicas/delete/
{
  "keys": ["jukebox/Musicas/Rock/song.mp3"]
}
```

---

## 6. Criar pasta (POST)

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
1. POST /musicas/sync/              → uma vez (ou quando o R2 mudar por fora) — admin
2. GET /musicas/                    → monta tree + lista a partir do PostgreSQL
3. Clicar pasta "Rock"              → GET /musicas/?prefix=Musicas/Rock/
4. Busca                            → GET /musicas/?q=love
5. Upload / excluir / criar pasta   → atualiza R2 e o cache — admin
6. Tocar arquivo                    → usar file.media_url no player
```

## Fluxo do app jukebox (só listar)

```
1. POST /maquinas/auth/             → guarda token
2. GET /musicas/?prefix=Musicas/    → Authorization: Maquina <token>
3. Player                           → item.media_url
```

## Notas

- Navegação e busca **não** listam o R2; usam o catálogo PostgreSQL
- Use `POST /musicas/sync/` ou o botão **Sincronizar biblioteca** no Admin após mudanças feitas direto no bucket
- Upload, exclusão, mover e criar pasta já atualizam o cache
- Campos `musicas` e `musicas_list` são somente áudio/vídeo, para o player
- `files` e `files_list` incluem também jpg/png (`media_type: image`)
