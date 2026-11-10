# Contrato 13 — PIX (QR Code) via Mercado Pago

## Identificação

| Campo | Valor |
|---|---|
| **ID** | `13-pix-mercadopago` |
| **Base path** | `/api/v1/pagamentos/` |
| **Status** | Implementado |

## Descrição

Gera **QR Code PIX** (copia e cola + imagem base64) usando a **conta Mercado Pago** configurada no backend. Quando o pagamento é aprovado, registra automaticamente um **crédito** na máquina (`origem: pix`).

### PostgreSQL

| Modelo | Uso |
|---|---|
| `MercadoPagoConfig` | Access token e opções da conta MP (Admin) |
| `PixCobranca` | Cobrança, QR, status e vínculo com `Credito` |

## Configuração

1. **Admin Django** → **Pagamentos** → **Contas Mercado Pago** → cadastre o **access token** (produção ou teste).
2. No [painel Mercado Pago](https://www.mercadopago.com.br/developers), configure o webhook:
   - `https://<seu-backend>/api/v1/pagamentos/webhook/mercadopago/`
3. Variáveis opcionais (Railway `.env`):
   - `MERCADOPAGO_ACCESS_TOKEN`
   - `MERCADOPAGO_NOTIFICATION_URL`
   - `MERCADOPAGO_WEBHOOK_BASE_URL` (ex.: `https://paineljukebox.h3ti.com.br`)

---

## 1. Gerar QR Code (`POST`)

```
POST /api/v1/pagamentos/pix/qrcode/
Authorization: Maquina <token>
```

```json
{
  "valor": 5.00,
  "descricao": "Créditos jukebox"
}
```

Admin com token Django pode enviar `maquina_id` no body.

### Response `201`

```json
{
  "id": 12,
  "maquina_id": 3,
  "maquina_nome": "Pesque Pague",
  "external_reference": "550e8400-e29b-41d4-a716-446655440000",
  "mp_payment_id": 123456789,
  "valor": "5.00",
  "valor_numero": 5.0,
  "status": "pendente",
  "qr_code": "00020126....",
  "qr_code_base64": "iVBORw0KGgo...",
  "ticket_url": "https://www.mercadopago.com.br/...",
  "expires_at": "2026-09-02T16:30:00+00:00",
  "credito_id": null,
  "created_at": "2026-09-02T16:00:00+00:00",
  "approved_at": null
}
```

| Campo | UI |
|---|---|
| `qr_code` | PIX copia e cola |
| `qr_code_base64` | Imagem do QR (`data:image/png;base64,...`) |
| `status` | `pendente` → aguardar; `aprovado` → crédito lançado |

---

## 2. Consultar cobrança (`GET`)

```
GET /api/v1/pagamentos/pix/{id}/
Authorization: Maquina <token> ou Token admin
```

---

## 3. Sincronizar com Mercado Pago (`GET` ou `POST`)

```
POST /api/v1/pagamentos/pix/{id}/sincronizar/
```

Atualiza o status no MP (polling do app enquanto o cliente paga).

---

## 4. Webhook Mercado Pago

```
POST /api/v1/pagamentos/webhook/mercadopago/?topic=payment&id=123456789
```

Sem autenticação (MP chama o servidor). Ao aprovar, cria `Credito` e preenche `credito_id` na cobrança.

---

## 5. CRUD conta MP (admin)

```
GET/POST/PATCH /api/v1/pagamentos/mercadopago/
Authorization: Token <admin>
```

`access_token` não retorna na leitura pública do serializer de listagem — use Admin ou `POST` com token no body.

---

## Erros comuns

| Código | Quando |
|---|---|
| `MP_NOT_CONFIGURED` | Sem conta ativa nem `MERCADOPAGO_ACCESS_TOKEN` |
| `MP_API_ERROR` | Mercado Pago recusou a cobrança |
| `UNAUTHORIZED` | Token de máquina inválido |

## Fluxo na jukebox

```
1. Usuário escolhe valor PIX
2. POST /pagamentos/pix/qrcode/ { valor }
3. Exibir QR (base64 ou copia e cola)
4. POST /pagamentos/pix/{id}/sincronizar/ a cada poucos segundos (ou aguardar webhook)
5. status=aprovado → crédito já está em POST /maquinas/creditos/ via registro automático
```
