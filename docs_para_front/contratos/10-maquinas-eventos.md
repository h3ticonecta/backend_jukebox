# Contrato 10 — Eventos e relatórios das máquinas

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `10-maquinas-eventos` |
| **Base path** | `/api/v1/maquinas/` |
| **Status** | Implementado |

## Descrição

A jukebox envia dois eventos para o PostgreSQL:

1. **Crédito** — dinheiro inserido na máquina
2. **Música tocada** — qual faixa da lista foi escolhida

Com esses dados o backend monta **faturamento** e **mais tocadas**.

## Autenticação

| Quem | Header |
|---|---|
| App da jukebox | `Authorization: Maquina <token>` (o token de `POST /maquinas/auth/`) |
| Admin / painel | `Authorization: Token <token-admin>` + `maquina_id` no body/query |

---

## 1. Registrar crédito (`POST`)

Quando o cliente inserir dinheiro:

```
POST /api/v1/maquinas/creditos/
Authorization: Maquina <token>
```

```json
{
  "valor": 5.00,
  "origem": "moeda",
  "observacao": ""
}
```

| Campo | Obrigatório | Descrição |
|---|---|---|
| `valor` | sim | Valor em R$ (ex: `5.00`) |
| `origem` | não | `moeda`, `nota`, `pix`, `credito`, `outro` (padrão: `moeda`) |
| `observacao` | não | Texto livre |
| `maquina_id` | só no token admin | Qual máquina recebeu o crédito |

### Response `201`

```json
{
  "id": 10,
  "maquina": 1,
  "maquina_nome": "Bar Central",
  "valor": "5.00",
  "origem": "moeda",
  "observacao": "",
  "created_at": "2026-09-02T16:20:00+00:00"
}
```

---

## 2. Registrar música escolhida (`POST`)

Quando o cliente escolher uma faixa da lista:

```
POST /api/v1/maquinas/tocadas/
Authorization: Maquina <token>
```

```json
{
  "musica_key": "Musicas/Rock/song.mp3",
  "musica_nome": "song.mp3",
  "titulo": "song",
  "pasta": "Musicas/Rock/",
  "media_type": "audio",
  "media_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/song.mp3",
  "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg",
  "valor": 1.00
}
```

`musica_key` é obrigatório (a chave da música na listagem). Os demais campos são snapshot para o relatório. `valor` é opcional (cobrança daquela faixa).

### Response `201`

Objeto da tocada com `id`, máquina e `created_at`.

---

## 3. Relatório de faturamento (`GET`)

Token **admin**.

```
GET /api/v1/maquinas/relatorio-faturamento/?inicio=2026-09-01&fim=2026-09-30&maquina_id=1
```

| Query | Descrição |
|---|---|
| `inicio` / `fim` | Datas `YYYY-MM-DD` (opcional) |
| `maquina_id` | Filtrar uma máquina (opcional) |

```json
{
  "faturamento_total": "120.00",
  "creditos_quantidade": 24,
  "tocadas_quantidade": 80,
  "por_origem": [{ "origem": "moeda", "total": "80.00", "quantidade": 16 }],
  "por_maquina": [{ "maquina_id": 1, "nome_jukebox": "Bar Central", "total": "120.00", "quantidade": 24 }],
  "por_dia": [{ "data": "2026-09-02", "total": "35.00", "quantidade": 7 }]
}
```

---

## 4. Relatório das mais tocadas (`GET`)

Token **admin**.

```
GET /api/v1/maquinas/relatorio-mais-tocadas/?inicio=2026-09-01&fim=2026-09-30&limit=20
```

```json
{
  "total_tocadas": 80,
  "ranking": [
    {
      "musica_key": "Musicas/Rock/song.mp3",
      "musica_nome": "song.mp3",
      "titulo": "song",
      "pasta": "Musicas/Rock/",
      "plays": 12,
      "cover_url": "https://pub-xxxxx.r2.dev/Musicas/Rock/cover.jpg"
    }
  ]
}
```

---

## Admin

- **Máquinas** → botão **Relatórios**
- **Créditos inseridos** e **Músicas tocadas** listam os eventos crus

---

## Fluxo no app da jukebox

```
1. POST /maquinas/auth/              → guarda token
2. Cliente insere R$ 5               → POST /maquinas/creditos/ { valor: 5 }
3. Cliente escolhe song.mp3          → POST /maquinas/tocadas/ { musica_key, titulo, cover_url, ... }
4. Painel consulta relatórios        → GET relatorio-faturamento / relatorio-mais-tocadas
```
