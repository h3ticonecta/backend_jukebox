import logging

import requests
from django.conf import settings

from pagamentos.exceptions import PagamentoServiceError

logger = logging.getLogger(__name__)

MP_API_BASE = 'https://api.mercadopago.com'


def mp_headers(access_token, idempotency_key=None):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    if idempotency_key:
        headers['X-Idempotency-Key'] = idempotency_key
    return headers


def criar_pagamento_pix(
    access_token,
    *,
    valor,
    description,
    external_reference,
    notification_url,
    payer_email,
    idempotency_key,
):
    payload = {
        'transaction_amount': float(valor),
        'description': description[:255],
        'payment_method_id': 'pix',
        'external_reference': external_reference,
        'notification_url': notification_url,
        'payer': {'email': payer_email},
    }
    headers = mp_headers(access_token, idempotency_key=idempotency_key)
    try:
        response = requests.post(
            f'{MP_API_BASE}/v1/payments',
            json=payload,
            headers=headers,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise PagamentoServiceError(
            f'Falha ao conectar ao Mercado Pago: {exc}',
            'MP_CONNECTION_ERROR',
        ) from exc

    try:
        body = response.json()
    except ValueError:
        body = {'message': response.text}

    if response.status_code not in (200, 201):
        message = body.get('message') or body.get('error') or response.text
        errors = body.get('cause') or body.get('errors')
        if errors:
            message = f'{message} — {errors}'
        logger.warning('Mercado Pago PIX error %s: %s', response.status_code, message)
        raise PagamentoServiceError(str(message)[:512], 'MP_API_ERROR')

    return body


def consultar_pagamento(access_token, payment_id):
    try:
        response = requests.get(
            f'{MP_API_BASE}/v1/payments/{payment_id}',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise PagamentoServiceError(
            f'Falha ao consultar pagamento: {exc}',
            'MP_CONNECTION_ERROR',
        ) from exc

    try:
        body = response.json()
    except ValueError:
        body = {}

    if response.status_code != 200:
        message = body.get('message') or response.text
        raise PagamentoServiceError(str(message)[:512], 'MP_API_ERROR')
    return body


def webhook_base_url():
    custom = getattr(settings, 'MERCADOPAGO_WEBHOOK_BASE_URL', '') or ''
    if custom:
        return custom.rstrip('/')
    allowed = settings.ALLOWED_HOSTS
    host = next((h for h in allowed if h and '.' in h and h != '*'), '')
    if host:
        return f'https://{host}'
    return ''
