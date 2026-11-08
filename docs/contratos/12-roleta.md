# Contrato 12 — Configuração da Roleta (por máquina)

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `12-roleta` |
| **Base path** | `/api/v1/maquinas/` |
| **Status** | Implementado |

## Descrição

Cada **máquina** tem uma configuração de roleta independente:

1. **Ativação** — toggle “Roleta ativada”
2. **Probabilidades (pesos)** — setor da roleta global (+2 músicas, +1, bônus 50%, tente novamente, não foi dessa vez)
3. **Regras** — créditos mínimos para girar; limite diário de prêmio +2 músicas (%)
4. **Faixas por valor inserido** — R$ 5 / 10 / 20 / … com giros liberados e lista de prêmios ponderados

Também editável no **Django Admin** em **Modificar máquina** (bloco “Configuração da Roleta”) e em **Máquinas → Configurações da roleta**.

### PostgreSQL

| Modelo | Tabela |
|---|---|
| `RoletaConfig` | Uma linha por máquina (`maquina_id` UNIQUE) |
| `RoletaFaixaValor` | Faixa de valor + giros |
| `RoletaPremioFaixa` | Prêmios da faixa (`tipo`, `quantidade`, `peso`) |

## Autenticação

| Endpoint | Auth |
|---|---|
| `GET/PUT/PATCH /maquinas/{id}/roleta/` | Token **admin** |
| `GET /maquinas/roleta/` | `Authorization: Maquina <token>` |

---

## 1. Admin — ler / gravar (`GET`, `PUT`, `PATCH`)

```
GET /api/v1/maquinas/3/roleta/
PUT /api/v1/maquinas/3/roleta/
PATCH /api/v1/maquinas/3/roleta/
Authorization: Token <token-admin>
```

### Response `200` (exemplo)

```json
{
  "maquina_id": 3,
  "nome_jukebox": "Pesque Pague",
  "ativada": true,
  "probabilidades": {
    "premio_mais_2_musicas": 1,
    "premio_mais_1_musica": 5,
    "bonus_recarga_50pct": 1,
    "tente_novamente": 40,
    "nao_foi_dessa_vez": 30,
    "resumo": {
      "total_pesos": 77,
      "chance_usuario_ganhar_percent": 9.1,
      "vantagem_sistema_percent": 90.9
    }
  },
  "regras": {
    "creditos_minimos_girar": 5,
    "max_premio_mais_2_musicas_dia_percent": 10
  },
  "faixas_valor": [
    {
      "id": 1,
      "valor": "5.00",
      "valor_numero": 5.0,
      "giros_liberados": 1,
      "ordem": 0,
      "premios": [
        {
          "id": 1,
          "tipo": "musica_gratis",
          "tipo_label": "Música grátis",
          "quantidade": 2,
          "peso": 10,
          "ordem": 0
        }
      ]
    }
  ],
  "updated_at": "2026-09-02T16:00:00+00:00"
}
```

### Body `PUT` / `PATCH`

```json
{
  "ativada": true,
  "probabilidades": {
    "premio_mais_2_musicas": 1,
    "premio_mais_1_musica": 5,
    "bonus_recarga_50pct": 1,
    "tente_novamente": 40,
    "nao_foi_dessa_vez": 30
  },
  "regras": {
    "creditos_minimos_girar": 5,
    "max_premio_mais_2_musicas_dia_percent": 10
  },
  "faixas_valor": [
    {
      "valor": "5.00",
      "giros_liberados": 1,
      "premios": [
        { "tipo": "musica_gratis", "quantidade": 2, "peso": 10 },
        { "tipo": "giro_extra", "quantidade": 1, "peso": 10 },
        { "tipo": "sem_premio", "quantidade": 1, "peso": 10 }
      ]
    }
  ]
}
```

| `tipo` (prêmio da faixa) | Significado |
|---|---|
| `musica_gratis` | Músicas grátis |
| `giro_extra` | Giros extras |
| `sem_premio` | Sem prêmio |

Ao enviar `faixas_valor`, a lista **substitui** as faixas anteriores (comportamento igual ao painel SPA).

---

## 2. Jukebox — consulta (`GET`)

```
GET /api/v1/maquinas/roleta/
Authorization: Maquina <token>
```

- `ativada: false` → resumo mínimo.
- `ativada: true` → mesmo JSON do admin (sem exigir `id` nas faixas para lógica do app).

---

## Notas

- Nova máquina ganha config padrão (pesos e faixas R$ 5–100) automaticamente.
- Tipos `sem_premio` com `quantidade: 1` — exibição no front como “-”.
- Prêmios **cumulativos** por faixa maior (regra de negócio no app): o backend armazena cada faixa; o front aplica a regra de cumulatividade descrita no print.
