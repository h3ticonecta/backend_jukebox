import logging
import re
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from maquinas.models import Credito, CreditoOrigem, Maquina
from pagamentos.exceptions import PagamentoServiceError
from pagamentos.mercadopago_client import (
    consultar_pagamento,
    criar_pagamento_pix,
    webhook_base_url,
)
from pagamentos.models import MercadoPagoConfig, PixCobranca

logger = logging.getLogger(__name__)


def notificacao_e_pagamento(topic):
    if not topic:
        return True
    base = str(topic).lower().strip().split('.')[0]
    return base == 'payment'


def get_mercadopago_config():
    config = MercadoPagoConfig.objects.filter(is_active=True).order_by('-updated_at').first()
    if config and config.access_token.strip():
        return config
    token = (getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None) or '').strip()
    if token:
        return MercadoPagoConfig(
            access_token=token,
            usar_sandbox=False,
            is_active=True,
            nome='variável de ambiente',
        )
    raise PagamentoServiceError(
        'Nenhuma conta Mercado Pago ativa. Cadastre em Admin → Contas Mercado Pago '
        'ou defina MERCADOPAGO_ACCESS_TOKEN.',
        'MP_NOT_CONFIGURED',
    )


def notification_url(config):
    override = (config.webhook_url or '').strip() if config.pk else ''
    if override:
        return override
    env_url = (getattr(settings, 'MERCADOPAGO_NOTIFICATION_URL', None) or '').strip()
    if env_url:
        return env_url
    base = webhook_base_url()
    if not base:
        return ''
    return f'{base}/api/v1/pagamentos/webhook/mercadopago/'


def payer_email(maquina):
    slug = re.sub(r'[^a-zA-Z0-9]', '', maquina.usuario or str(maquina.pk))[:32]
    return f'jukebox-{maquina.id}-{slug}@cliente.jukebox'


def map_mp_status(mp_status):
    if mp_status == 'approved':
        return PixCobranca.Status.APROVADO
    if mp_status in ('rejected', 'cancelled'):
        return PixCobranca.Status.REJEITADO
    if mp_status == 'refunded':
        return PixCobranca.Status.CANCELADO
    if mp_status in ('pending', 'in_process', 'authorized'):
        return PixCobranca.Status.PENDENTE
    if mp_status in ('charged_back',):
        return PixCobranca.Status.CANCELADO
    return PixCobranca.Status.PENDENTE


def extract_qr_data(mp_body):
    poi = (mp_body.get('point_of_interaction') or {})
    tx = poi.get('transaction_data') or {}
    return {
        'qr_code': tx.get('qr_code') or '',
        'qr_code_base64': tx.get('qr_code_base64') or '',
        'ticket_url': tx.get('ticket_url') or mp_body.get('transaction_details', {}).get('external_resource_url') or '',
    }


def parse_mp_datetime(value):
    if not value:
        return None
    if isinstance(value, str):
        dt = parse_datetime(value.replace('Z', '+00:00'))
        if dt:
            return dt
    return None


def pix_cobranca_payload(cobranca):
    return {
        'id': cobranca.id,
        'maquina_id': cobranca.maquina_id,
        'maquina_nome': cobranca.maquina.nome_jukebox,
        'external_reference': str(cobranca.external_reference),
        'mp_payment_id': cobranca.mp_payment_id,
        'valor': f'{cobranca.valor:.2f}',
        'valor_numero': float(cobranca.valor),
        'status': cobranca.status,
        'qr_code': cobranca.qr_code,
        'qr_code_base64': cobranca.qr_code_base64,
        'ticket_url': cobranca.ticket_url,
        'expires_at': cobranca.expires_at.isoformat() if cobranca.expires_at else None,
        'credito_id': cobranca.credito_id,
        'created_at': cobranca.created_at.isoformat(),
        'approved_at': cobranca.approved_at.isoformat() if cobranca.approved_at else None,
    }


def criar_cobranca_pix(maquina, valor, descricao=None):
    if valor <= 0:
        raise PagamentoServiceError('Valor deve ser maior que zero.', 'INVALID_AMOUNT')

    config = get_mercadopago_config()
    if not isinstance(maquina, Maquina):
        maquina = Maquina.objects.get(pk=maquina)

    description = descricao or f'Crédito jukebox — {maquina.nome_jukebox}'
    notif = notification_url(config)

    cobranca = PixCobranca.objects.create(
        maquina=maquina,
        config=config if config.pk else None,
        valor=Decimal(valor),
        descricao=description[:255],
        status=PixCobranca.Status.PENDENTE,
    )

    try:
        mp_body = criar_pagamento_pix(
            config.access_token,
            valor=cobranca.valor,
            description=description,
            external_reference=str(cobranca.external_reference),
            notification_url=notif,
            payer_email=payer_email(maquina),
            idempotency_key=str(cobranca.external_reference),
        )
    except PagamentoServiceError as exc:
        cobranca.status = PixCobranca.Status.ERRO
        cobranca.ultimo_erro = exc.message
        cobranca.save(update_fields=['status', 'ultimo_erro', 'updated_at'])
        raise

    qr = extract_qr_data(mp_body)
    cobranca.mp_payment_id = mp_body.get('id')
    cobranca.qr_code = qr['qr_code']
    cobranca.qr_code_base64 = qr['qr_code_base64']
    cobranca.ticket_url = qr['ticket_url'][:512] if qr['ticket_url'] else ''
    cobranca.mp_status_detail = mp_body.get('status_detail') or ''
    cobranca.status = map_mp_status(mp_body.get('status') or 'pending')
    cobranca.raw_response = mp_body
    cobranca.expires_at = parse_mp_datetime(
        (mp_body.get('date_of_expiration')),
    ) or (timezone.now() + timedelta(minutes=30))
    cobranca.save()

    if cobranca.status == PixCobranca.Status.APROVADO:
        registrar_credito_pix(cobranca)

    return cobranca


@transaction.atomic
def registrar_credito_pix(cobranca):
    cobranca = PixCobranca.objects.select_for_update().select_related('maquina').get(pk=cobranca.pk)
    if cobranca.credito_id:
        return cobranca.credito
    if cobranca.status != PixCobranca.Status.APROVADO:
        return None

    credito = Credito.objects.create(
        maquina=cobranca.maquina,
        valor=cobranca.valor,
        origem=CreditoOrigem.PIX,
        observacao=f'PIX MP #{cobranca.mp_payment_id or cobranca.id}',
    )
    cobranca.credito = credito
    cobranca.approved_at = cobranca.approved_at or timezone.now()
    cobranca.save(update_fields=['credito', 'approved_at', 'updated_at'])
    return credito


def atualizar_cobranca_pelo_mp(cobranca, mp_body):
    cobranca.status = map_mp_status(mp_body.get('status') or '')
    cobranca.mp_status_detail = mp_body.get('status_detail') or ''
    cobranca.raw_response = mp_body
    if cobranca.status == PixCobranca.Status.APROVADO:
        cobranca.approved_at = cobranca.approved_at or timezone.now()
    cobranca.save()
    if cobranca.status == PixCobranca.Status.APROVADO:
        registrar_credito_pix(cobranca)
    return cobranca


def sincronizar_cobranca(cobranca):
    if not cobranca.mp_payment_id:
        raise PagamentoServiceError('Cobrança sem ID no Mercado Pago.', 'MISSING_MP_ID')
    config = cobranca.config or get_mercadopago_config()
    mp_body = consultar_pagamento(config.access_token, cobranca.mp_payment_id)
    return atualizar_cobranca_pelo_mp(cobranca, mp_body)


def processar_webhook_mp(*, payment_id=None, topic=None):
    if topic and not notificacao_e_pagamento(topic):
        return {'ignored': True, 'message': f'Tópico ignorado: {topic}'}
    if not payment_id:
        raise PagamentoServiceError('Notificação sem ID de pagamento.', 'WEBHOOK_INVALID')

    config = get_mercadopago_config()
    try:
        mp_body = consultar_pagamento(config.access_token, payment_id)
    except PagamentoServiceError as exc:
        logger.warning(
            'Webhook MP: não foi possível consultar pagamento %s (%s).',
            payment_id,
            exc.code,
        )
        return {
            'ignored': True,
            'payment_id': payment_id,
            'code': exc.code,
            'message': exc.message,
        }

    cobranca = PixCobranca.objects.filter(mp_payment_id=payment_id).first()
    if cobranca is None:
        ext = mp_body.get('external_reference')
        if ext:
            cobranca = PixCobranca.objects.filter(external_reference=ext).first()
    if cobranca is None:
        logger_msg = f'Webhook MP: pagamento {payment_id} sem cobrança local.'
        return {'ignored': True, 'message': logger_msg}

    atualizar_cobranca_pelo_mp(cobranca, mp_body)
    return pix_cobranca_payload(cobranca)
