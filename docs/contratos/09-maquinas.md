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
| `GET` / `PUT` / `PATCH` | `/api/v1/maquinas/{id}/roleta/` | Configuração da roleta — [contrato 12](./12-roleta.md) |

### Schema — leitura

```json
{
  "id": 1,
  "nome_jukebox": "Bar Central",
  "usuario": "jukebox01",
  "is_active": true,
  "teclas": [
    { "acao": "cima", "label": "Cima", "tecla": "Q" },
    { "acao": "baixo", "label": "Baixo", "tecla": "W" },
    { "acao": "esquerda", "label": "Esquerda", "tecla": "E" },
    { "acao": "direita", "label": "Direita", "tecla": "R" },
    { "acao": "credito", "label": "Crédito", "tecla": "K" },
    { "acao": "hits", "label": "HITS", "tecla": "I" },
    { "acao": "fila", "label": "Fila", "tecla": "F" },
    { "acao": "pular", "label": "Pular", "tecla": "P" },
    { "acao": "tocar_cd", "label": "Tocar CD", "tecla": "C" },
    { "acao": "vol", "label": "Vol", "tecla": "V" },
    { "acao": "cancelar", "label": "Cancelar", "tecla": "Enter" }
  ],
  "last_login_at": "2026-09-02T16:40:00+00:00",
  "created_at": "2026-09-02T16:00:00+00:00",
  "updated_at": "2026-09-02T16:40:00+00:00"
}
```

### Schema — atualizar teclas (`PATCH` admin)

Somente o **admin** altera teclas (Admin Django ou API com token admin):

```json
{
  "teclas": [
    { "acao": "credito", "tecla": "K" },
    { "acao": "cima", "tecla": "Q" }
  ]
}
```

Envie só as ações que mudaram ou a lista completa. `label` é fixo no backend; o front exibe `label` + `tecla`.

| `acao` | Label padrão | Tecla padrão |
|---|---|---|
| `cima` | Cima | `Q` |
| `baixo` | Baixo | `W` |
| `esquerda` | Esquerda | `E` |
| `direita` | Direita | `R` |
| `credito` | Crédito | `K` |
| `hits` | HITS | `I` |
| `fila` | Fila | `F` |
| `pular` | Pular | `P` |
| `tocar_cd` | Tocar CD | `C` |
| `vol` | Vol | `V` |
| `cancelar` | Cancelar | `Enter` |

`vol_mais` / `vol_menos` são **legado** — na migração viram `vol` (prioridade: tecla de `vol`, senão `vol_mais`, senão `vol_menos`).

### Volume — um botão na máquina (`acao`: `vol`)

Login (`POST /auth/`) e config (`GET /config/`) incluem:

```json
{
  "comportamento_volume": {
    "modo": "unico_botao",
    "clique_unico": "aumentar",
    "cliques_repetidos": "diminuir",
    "pressionar_segurar": "diminuir_continuo"
  }
}
```

| Gestão no app | Efeito sugerido |
|---|---|
| Um clique na tecla `vol` | Aumenta o volume |
| Vários cliques em sequência (debounce no front) | Diminui o volume |
| Manter pressionado | Diminui o volume de forma contínua |

O backend só define **qual tecla** é `vol`; tempos e limiares ficam no frontend.

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
  "token": "a1b2c3d4e5f6...",
  "teclas": [
    { "acao": "cima", "label": "Cima", "tecla": "Q" },
    { "acao": "credito", "label": "Crédito", "tecla": "K" }
  ],
  "comportamento_volume": {
    "modo": "unico_botao",
    "clique_unico": "aumentar",
    "cliques_repetidos": "diminuir",
    "pressionar_segurar": "diminuir_continuo"
  }
}
```

O front deve guardar `id`, `nome_jukebox`, `token`, `teclas` e `comportamento_volume` no dispositivo.

---

## 3. Configuração da máquina (`GET /config/`)

Retorna teclas atualizadas sem novo login.

```
GET /api/v1/maquinas/config/
Authorization: Maquina <token>
```

```json
{
  "id": 1,
  "nome_jukebox": "Bar Central",
  "usuario": "jukebox01",
  "teclas": [
    { "acao": "credito", "label": "Crédito", "tecla": "K" },
    { "acao": "vol", "label": "Vol", "tecla": "V" }
  ],
  "comportamento_volume": {
    "modo": "unico_botao",
    "clique_unico": "aumentar",
    "cliques_repetidos": "diminuir",
    "pressionar_segurar": "diminuir_continuo"
  }
}
```

---

### Erros (`POST /auth/`)

| HTTP | Código | Quando |
|---|---|---|
| `400` | `INVALID_CREDENTIALS` | Usuário ou senha inválidos |
| `403` | `MACHINE_INACTIVE` | Máquina cadastrada como inativa |

---

## Cadastro no Django Admin

`/admin/` → **Máquinas** → seção **Teclas** para configurar cada atalho.

---

## Notas para o frontend

- Token do **admin** (`/api/v1/auth/token/`) gerencia o cadastro
- Token da **máquina** (`/api/v1/maquinas/auth/`) identifica qual jukebox está logada
- `teclas` vem no login e em `GET /maquinas/config/` — exibir no app; **só o admin altera**
- Tecla `credito`: o front abre inserção de crédito; confirma com `POST /maquinas/creditos/`
- Tecla `tocar_cd` (**Tocar CD**): o front enfileira ou toca todas as faixas da pasta/CD selecionado (comportamento no app)
- Tecla `vol` (**Vol**): um único atalho; use `comportamento_volume` da API para clique / cliques repetidos / segurar
- Eventos de crédito e música tocada: [contrato 10](./10-maquinas-eventos.md)
- `usuario` é único
- Não envie a senha em telas de listagem; ela só entra no cadastro e no login
