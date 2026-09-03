# Pacote de integração — Frontend Jukebox

Documentação copiada do backend para o time de frontend. Repositório: `h3ticonecta/backend_jukebox` (branch `dev`).

## Comece por aqui

1. [ambientes.md](./ambientes.md) — URLs e variáveis de ambiente
2. [integracao-frontend.md](./integracao-frontend.md) — guia prático com exemplos TypeScript
3. [contratos/README.md](./contratos/README.md) — índice dos contratos de API

## Base URL (dev)

```
https://backendjukebox-dev.up.railway.app
```

```env
VITE_API_BASE_URL=https://backendjukebox-dev.up.railway.app
```

## App jukebox (prioridade)

| Contrato | Endpoint | Auth |
|---|---|---|
| [09-maquinas](./contratos/09-maquinas.md) | `POST /api/v1/maquinas/auth/` | Público (usuario + senha) |
| [06-musicas-listar](./contratos/06-musicas-listar.md) | `GET /api/v1/musicas/` | `Maquina <token>` |
| [10-maquinas-eventos](./contratos/10-maquinas-eventos.md) | `POST /creditos/`, `POST /tocadas/` | `Maquina <token>` |

Fluxo:

```
POST /maquinas/auth/     → guarda token
GET  /musicas/           → monta UI (musicas[], cover_url)
Player                   → item.media_url (URL pública R2)
POST /maquinas/creditos/ → dinheiro inserido
POST /maquinas/tocadas/  → faixa escolhida
```

## Painel admin / backoffice

| Contrato | Uso |
|---|---|
| [03-auth-token](./contratos/03-auth-token.md) | Login admin → `Authorization: Token ...` |
| [04-buckets-crud](./contratos/04-buckets-crud.md) | Cadastro bucket R2 |
| [05-bucket-objects](./contratos/05-bucket-objects.md) | Objetos no bucket |
| [06-musicas-listar](./contratos/06-musicas-listar.md) | Sync, upload, delete, move |
| [09-maquinas](./contratos/09-maquinas.md) | CRUD máquinas |
| [10-maquinas-eventos](./contratos/10-maquinas-eventos.md) | Relatórios |

## Utilitários

| Contrato | Endpoint |
|---|---|
| [01-service-info](./contratos/01-service-info.md) | `GET /` |
| [02-health-check](./contratos/02-health-check.md) | `GET /health/` |

## Autenticação

| Quem | Endpoint | Header |
|---|---|---|
| Admin | `POST /api/v1/auth/token/` | `Authorization: Token <token>` |
| Jukebox | `POST /api/v1/maquinas/auth/` | `Authorization: Maquina <token>` |

## CORS

No **backend** (Railway → Variables):

```
CORS_ALLOWED_ORIGINS=https://<url-do-front>,http://localhost:5173
```

## Não implementar agora

- Fila de reprodução (sem endpoint)
- Votação de músicas (sem endpoint)
- Login via `/admin/` (HTML Django, não API)
- Contratos 07 e 08 (legado — substituídos pelo 06)
