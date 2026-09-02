# Contrato 06 — Músicas (File Manager R2)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `06-musicas-file-manager` |
| **Base path** | `/api/v1/musicas/` |
| **Status** | Implementado |

## Descrição

A aba de músicas funciona como um **gerenciador de arquivos** do R2. Não é necessário cadastrar músicas separadamente — os arquivos são lidos diretamente do bucket na pasta `jukebox/Musicas/` (configurável no Admin).

Suporta `.mp3` (áudio) e `.mp4` (videoclipe).

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
  "root_path": "jukebox/Musicas/",
  "current_path": "jukebox/Musicas/Rock/",
  "parent_path": "jukebox/Musicas/",
  "breadcrumbs": [
    { "name": "Musicas", "path": "jukebox/Musicas/" },
    { "name": "Rock", "path": "jukebox/Musicas/Rock/" }
  ],
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
    { "name": "Pop", "path": "jukebox/Musicas/Pop/" }
  ],
  "files": [
    {
      "name": "song.mp3",
      "title": "song",
      "key": "jukebox/Musicas/Rock/song.mp3",
      "folder_path": "jukebox/Musicas/Rock/",
      "extension": ".mp3",
      "media_type": "audio",
      "media_url": "https://pub-xxxxx.r2.dev/jukebox/Musicas/Rock/song.mp3",
      "size": 5242880,
      "last_modified": "2026-09-01T18:00:00+00:00"
    }
  ],
  "files_list": [],
  "totals": {
    "folders": 5,
    "files": 120,
    "audio": 100,
    "video": 20
  }
}
```

### Uso no frontend

| Campo | Componente UI |
|---|---|
| `tree` | Árvore lateral (sidebar) |
| `breadcrumbs` | Barra de navegação |
| `folders` | Ícones de pasta na área principal |
| `files` | Lista de músicas/vídeos da pasta atual |
| `files_list` | Busca global em todas as pastas |

---

## 2. Upload (POST)

```
POST /api/v1/musicas/upload/
Content-Type: multipart/form-data
```

| Campo | Tipo | Descrição |
|---|---|---|
| `file` | file | Arquivo `.mp3` ou `.mp4` |
| `prefix` | string | Pasta destino (ex: `jukebox/Musicas/Rock/`) |

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
- Campos `musicas` e `musicas_list` mantidos como alias de `files` e `files_list`
