# Contrato 09 — Máquinas (Jukebox)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `09-maquinas` |
| **Base path** | `/api/v1/maquinas/` |
| **Status** | Implementado |

## Descrição

Cadastro das jukebox físicas (nome, usuário e senha) para vinculação do app. A senha é gravada com hash e **nunca** retorna nas listagens.

O login da máquina (`POST /auth/`) devolve um `token` próprio da jukebox, diferente do token do admin.

## Autenticação

| Endpoint | Auth |
|---|---|
| CRUD `/api/v1/maquinas/` | Token do **admin** (`POST /api/v1/auth/token/`) |
| `POST /api/v1/maquinas/auth/` | Pública (usuário + senha da máquina) |

---

## 1. CRUD (admin / backoffice)

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/v1/maquinas/` | Listar máquinas |
| `POST` | `/api/v1/maquinas/` | Cadastrar máquina |
| `GET` | `/api/v1/maquinas/{id}/` | Detalhar |
| `PUT` / `PATCH` | `/api/v1/maquinas/{id}/` | Atualizar |
| `DELETE` | `/api/v1/maquinas/{id}/` | Remover |

### Schema — leitura

```json
{
  "id": 1,
  "nome_jukebox": "Bar Central",
  "usuario": "jukebox01",
  "is_active": true,
  "last_login_at": "2026-09-02T16:40:00+00:00",
  "created_at": "2026-09-02T16:00:00+00:00",
  "updated_at": "2026-09-02T16:40:00+00:00"
}
```

### Schema — criar (`POST`)

```json
{
  "nome_jukebox": "Bar Central",
  "usuario": "jukebox01",
  "senha": "senha-da-maquina",
  "is_active": true
}
```

Em `PUT`/`PATCH`, `senha` é opcional. Se enviada, a senha e o token da máquina são renovados.

---

## 2. Vincular máquina (`POST /auth/`)

Usado pelo app da jukebox no primeiro acesso.

```
POST /api/v1/maquinas/auth/
Content-Type: application/json
```

```json
{
  "usuario": "jukebox01",
  "senha": "senha-da-maquina"
}
```

### Response — `200 OK`

```json
{
  "id": 1,
  "nome_jukebox": "Bar Central",
  "usuario": "jukebox01",
  "token": "a1b2c3d4e5f6..."
}
```

O front deve guardar `id`, `nome_jukebox` e `token` no dispositivo.

### Erros

| HTTP | Código | Quando |
|---|---|---|
| `400` | `INVALID_CREDENTIALS` | Usuário ou senha inválidos |
| `403` | `MACHINE_INACTIVE` | Máquina cadastrada como inativa |

---

## Cadastro no Django Admin

`/admin/` → **Máquinas** → Adicionar. Campos: nome da jukebox, usuário, senha.

---

## Notas para o frontend

- Token do **admin** (`/api/v1/auth/token/`) gerencia o cadastro
- Token da **máquina** (`/api/v1/maquinas/auth/`) identifica qual jukebox está logada
- Eventos de crédito e música tocada: [contrato 10](./10-maquinas-eventos.md)
- `usuario` é único
- Não envie a senha em telas de listagem; ela só entra no cadastro e no login
