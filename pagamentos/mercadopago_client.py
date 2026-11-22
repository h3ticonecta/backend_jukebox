import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

import requests
from django.conf import settings
from django.utils import timezone

from pagamentos.exceptions import PagamentoServiceError

logger = logging.getLogger(__name__)

MP_API_BASE = 'https://api.mercadopago.com'
MP_TZ = ZoneInfo('America/Sao_Paulo')


def format_date_of_expiration(dt):
    """ISO 8601 com offset para o Mercado Pago (ex.: 2026-11-22T17:30:00.000-03:00)."""
    local = dt.astimezone(MP_TZ)
    base = local.strftime('%Y-%m-%dT%H:%M:%S.000')
    offset = local.strftime('%z')
    if len(offset) == 5:
        offset = f'{offset[:3]}:{offset[3:]}'
    return f'{base}{offset}'


def normalizar_expiracao_segundos(expiracao_segundos):
    """
    Retorna (solicitado, segundos_enviados_ao_mp).
    O MP exige no mínimo 30 minutos na date_of_expiration do PIX.
    """
    default = int(getattr(settings, 'MERCADOPAGO_PIX_EXPIRACAO_SEGUNDOS', 300))
    solicitado = default if expiracao_segundos is None else int(expiracao_segundos)
    if solicitado < 1:
        solicitado = default
    min_mp = int(getattr(settings, 'MERCADOPAGO_PIX_EXPIRACAO_MIN_SEGUNDOS', 30 * 60))
    max_mp = int(getattr(settings, 'MERCADOPAGO_PIX_EXPIRACAO_MAX_SEGUNDOS', 30 * 86400))
    enviado = max(min_mp, min(solicitado, max_mp))
    return solicitado, enviado


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
    expiracao_segundos=None,
):
    _, segundos_mp = normalizar_expiracao_segundos(expiracao_segundos)
    expira_em = timezone.now() + timedelta(seconds=segundos_mp)
    payload = {
        'transaction_amount': float(valor),
        'description': description[:255],
        'payment_method_id': 'pix',
        'external_reference': external_reference,
        'notification_url': notification_url,
        'payer': {'email': payer_email},
        'date_of_expiration': format_date_of_expiration(expira_em),
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
