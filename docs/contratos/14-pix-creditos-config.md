# Contrato 14 — Configuração de créditos PIX

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `14-pix-creditos-config` |
| **Base path** | `/api/v1/pagamentos/pix-creditos/` |
| **Status** | Implementado |

## Descrição

Define os **valores PIX** oferecidos no modal da jukebox (ex.: R$ 5, R$ 10, …) e a **quantidade de créditos** concedida na máquina quando o pagamento é aprovado.

Editável no **Django Admin** → **Pagamentos** → **créditos (configuração)** (item abaixo de *Contas Mercado Pago*).

### PostgreSQL

| Modelo | Uso |
|---|---|
| `PixCreditoOpcao` | `valor_pix` (único), `quantidade_creditos`, `ordem`, `ativo` |
| `PixCobranca.creditos_concedidos` | Congelado ao gerar o QR |

Ao aprovar o PIX, o crédito inserido em `maquinas.Credito` usa `creditos_concedidos` (não o valor em reais pago).

---

## 1. Jukebox — listar opções ativas

```
GET /api/v1/pagamentos/pix-creditos/opcoes/
Authorization: Maquina <token>
```

### Response `200`

```json
{
  "opcoes": [
    {
      "id": 1,
      "valor_pix": "5.00",
      "valor_pix_numero": 5.0,
      "quantidade_creditos": 5,
      "ordem": 1
    },
    {
      "id": 2,
      "valor_pix": "10.00",
      "valor_pix_numero": 10.0,
      "quantidade_creditos": 12,
      "ordem": 2
    }
  ]
}
```

Use esta lista para montar os botões do modal PIX e o texto “R$ X → N créditos”.

---

## 2. Admin — CRUD completo

```
GET    /api/v1/pagamentos/pix-creditos/
POST   /api/v1/pagamentos/pix-creditos/
GET    /api/v1/pagamentos/pix-creditos/{id}/
PUT    /api/v1/pagamentos/pix-creditos/{id}/
PATCH  /api/v1/pagamentos/pix-creditos/{id}/
DELETE /api/v1/pagamentos/pix-creditos/{id}/
Authorization: Token <token-admin>
```

### Body (criar/atualizar)

```json
{
  "valor_pix": "5.00",
  "quantidade_creditos": 8,
  "ordem": 1,
  "ativo": true
}
```

A jukebox também pode chamar `GET /api/v1/pagamentos/pix-creditos/` (somente registros `ativo`) com header `Maquina`.

---

## 3. Valores padrão (migração)

| Valor PIX | Créditos iniciais |
|---|---|
| R$ 5,00 | 5 |
| R$ 10,00 | 10 |
| R$ 20,00 | 20 |
| R$ 50,00 | 50 |
| R$ 100,00 | 100 |

---

## Notas para o frontend

1. Antes de abrir o modal PIX, carregue `GET .../opcoes/` e use `valor_pix_numero` no `POST .../pix/qrcode/`.
2. A resposta do QR inclui `quantidade_creditos` com o que será creditado após aprovação.
3. Relação R$ 1 = 1 crédito **não** é fixa; segue apenas a configuração do backend.
