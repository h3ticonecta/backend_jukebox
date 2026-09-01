# Contrato 08 — Músicas (Upload)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `08-musicas-upload` |
| **Método** | `POST` |
| **Path** | `/api/v1/musicas/{id}/upload/` |
| **Status** | Implementado |

## Descrição

Envia o arquivo de áudio para o R2 e atualiza os metadados da música (`storage_key`, `file_size`, `content_type`).

## Autenticação

Obrigatória — `Authorization: Token <token>`

## Request

```
POST /api/v1/musicas/{id}/upload/
Content-Type: multipart/form-data
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `file` | `file` | Sim | Arquivo de áudio |

### Extensões permitidas

`.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`

## Response — Sucesso (`200 OK`)

Retorna o objeto completo da música com `storage_key`, `audio_url` e metadados atualizados.

```json
{
  "id": 1,
  "title": "Minha Música",
  "storage_key": "musicas/1/song.mp3",
  "audio_url": "https://pub-xxxxx.r2.dev/musicas/1/song.mp3",
  "file_size": 5242880,
  "content_type": "audio/mpeg"
}
```

## Response — Erros

| Código | Quando |
|---|---|
| `400` | Extensão inválida ou erro no upload R2 |
| `401` | Token ausente ou inválido |
| `404` | Música não encontrada |

## Exemplo

```bash
curl -X POST https://backendjukebox-dev.up.railway.app/api/v1/musicas/1/upload/ \
  -H "Authorization: Token <token>" \
  -F "file=@song.mp3"
```

## Fluxo recomendado no frontend

1. `POST /api/v1/musicas/` — criar metadados
2. `POST /api/v1/musicas/{id}/upload/` — enviar arquivo
3. Usar `audio_url` da resposta no player

## Notas

- O `storage_key` é gerado automaticamente: `musicas/{id}/{nome-arquivo}`
- Re-upload substitui o arquivo anterior no R2 (nova key baseada no nome do arquivo)
