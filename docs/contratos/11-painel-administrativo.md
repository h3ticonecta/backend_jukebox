# Contrato 11 — Painel Administrativo (Dashboard)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `11-painel-administrativo` |
| **Base path** | `/api/v1/maquinas/painel-administrativo/` |
| **Frontend** | `https://jukebox.h3ti.com.br/#/admin` (rota SPA; autenticação via token admin) |
| **Status** | Implementado |

## Descrição

Alimenta a página **Painel Administrativo** (cards de resumo, faturamento por máquina e gráfico de barras).

Não há tabelas novas: os dados vêm do PostgreSQL já existente:

| Tabela / modelo | Uso no painel |
|---|---|
| `Maquina` | Máquinas ativas, lista para filtros e cards |
| `Credito` | Faturamento total e créditos vendidos (`POST /maquinas/creditos/` na jukebox) |
| `MusicaTocada` | Quantidade de músicas tocadas (`POST /maquinas/tocadas/`) |

## Autenticação

| Header | Quem |
|---|---|
| `Authorization: Token <token-admin>` | Painel `/#/admin` após `POST /api/v1/auth/token/` |

## Endpoint

```
GET /api/v1/maquinas/painel-administrativo/
```

### Query (filtros da UI)

| Param | Descrição |
|---|---|
| `periodo` ou `preset` | `tudo` (padrão), `hoje`, `semana`, `mes` — aliases: `today`, `esta_semana`, `este_mes` |
| `inicio` / `data_inicio` | `YYYY-MM-DD` — se informado com `fim`, ignora o cálculo do preset |
| `fim` / `data_fim` | `YYYY-MM-DD`, inclusivo |
| `maquina_id` | Filtra uma máquina |
| `status` | `todos` (padrão), `ativo`, `inativo` — restringe máquinas e eventos |

### Response `200`

```json
{
  "painel": "administrativo",
  "periodo": {
    "preset": "tudo",
    "data_inicio": null,
    "data_fim": null
  },
  "filtros": {
    "maquina_id": null,
    "status": "todos"
  },
  "resumo": {
    "faturamento_total": "2188.00",
    "faturamento_total_numero": 2188.0,
    "creditos_vendidos": 3177,
    "musicas_tocadas": 1000,
    "maquinas_ativas": 3
  },
  "faturamento_por_maquina": [
    {
      "maquina_id": 3,
      "nome_jukebox": "Pesque Pague",
      "faturamento": "1423.00",
      "faturamento_numero": 1423.0,
      "creditos": 2108,
      "is_active": true
    },
    {
      "maquina_id": 1,
      "nome_jukebox": "Firma",
      "faturamento": "193.00",
      "faturamento_numero": 193.0,
      "creditos": 288,
      "is_active": true
    }
  ],
  "grafico_faturamento_por_maquina": [
    {
      "maquina_id": 3,
      "nome_jukebox": "Pesque Pague",
      "valor": 1423.0
    }
  ],
  "maquinas_opcoes": [
    { "id": 1, "nome_jukebox": "Firma", "is_active": true },
    { "id": 2, "nome_jukebox": "Jukebox PC Gustavo", "is_active": true }
  ]
}
```

### Mapeamento UI → API

| Componente no print | Campo |
|---|---|
| Faturamento Total | `resumo.faturamento_total` (exibir em R$) |
| Créditos Vendidos | `resumo.creditos_vendidos` |
| Músicas Tocadas | `resumo.musicas_tocadas` |
| Máquinas Ativas | `resumo.maquinas_ativas` (sempre total global de `is_active=true`) |
| Cards “Faturamento por Máquina” | `faturamento_por_maquina[]` |
| Gráfico de barras | `grafico_faturamento_por_maquina[]` (eixo Y = `valor`) |
| Combo “Todas as máquinas” | `maquinas_opcoes` + query `maquina_id` |
| Filtros de período | query `periodo=hoje` \| `semana` \| `mes` \| `tudo` |
| Combo status | query `status=ativo` \| `inativo` \| `todos` |
| Exportar PDF | Somente no frontend (gerar a partir deste JSON) |

### Abas do painel (outras rotas)

| Aba | API existente |
|---|---|
| Dashboard | Este contrato |
| Máquinas | [09-maquinas.md](./09-maquinas.md) `CRUD /api/v1/maquinas/` |
| Configurações | Buckets / músicas — contratos 04–06 |
| Usuários | Token admin via Django `User` (a definir no front ou Admin Django) |

## Exemplo

```bash
curl "https://backendjukebox-dev.up.railway.app/api/v1/maquinas/painel-administrativo/?periodo=mes" \
  -H "Authorization: Token <token-admin>"
```

## Notas

- `faturamento_total` soma apenas **créditos inseridos**; músicas tocadas entram só no contador `musicas_tocadas`.
- Máquinas sem vendas no período aparecem com `faturamento` `0.00` e `creditos` `0`.
- CORS: inclua `https://jukebox.h3ti.com.br` em `CORS_ALLOWED_ORIGINS` no backend.
