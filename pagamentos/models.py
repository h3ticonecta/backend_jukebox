import uuid

from django.db import models

from maquinas.models import Credito, Maquina


DEFAULT_MP_PAYER_EMAIL = 'gustavo.santos@h3ti.com.br'

class PixCreditoOpcao(models.Model):
    """Valor PIX oferecido na jukebox e quantidade de créditos concedidos ao pagar."""

    valor_pix = models.DecimalField(
        'valor PIX (R$)',
        max_digits=10,
        decimal_places=2,
        unique=True,
    )
    quantidade_creditos = models.PositiveIntegerField(
        'quantidade de créditos',
        help_text='Créditos inseridos na máquina quando o PIX deste valor for aprovado.',
    )
    ordem = models.PositiveSmallIntegerField('ordem', default=0)
    ativo = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'configuração créditos'
        verbose_name_plural = 'créditos (configuração)'
        ordering = ['ordem', 'valor_pix']

    def __str__(self):
        return f'R$ {self.valor_pix} → {self.quantidade_creditos} crédito(s)'


class MercadoPagoConfig(models.Model):
    """Credenciais da conta Mercado Pago (PIX)."""

    nome = models.CharField(
        'identificação',
        max_length=120,
        default='Conta principal',
        help_text='Rótulo interno (ex.: conta produção H3TI).',
    )
    access_token = models.CharField(
        'access token',
        max_length=512,
        help_text='Token de produção ou teste do Mercado Pago.',
    )
    public_key = models.CharField('public key', max_length=128, blank=True)
    id_conta = models.CharField('ID da conta MP', max_length=64, blank=True)
    usar_sandbox = models.BooleanField('modo teste (sandbox)', default=False)
    is_active = models.BooleanField('ativo', default=True)
    webhook_url = models.URLField(
        'URL de notificação (override)',
        max_length=512,
        blank=True,
        help_text='Opcional. Se vazio, usa a URL pública do backend + /api/v1/pagamentos/webhook/mercadopago/',
    )
    email_pagador_padrao = models.EmailField(
        'e-mail padrão do pagador',
        max_length=254,
        default=DEFAULT_MP_PAYER_EMAIL,
        help_text='Obrigatório para a API do Mercado Pago (payer.email). Não use o usuário da jukebox.',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'conta Mercado Pago'
        verbose_name_plural = 'contas Mercado Pago'
        ordering = ['-is_active', 'nome']

    def __str__(self):
        suffix = ' (teste)' if self.usar_sandbox else ''
        return f'{self.nome}{suffix}'


class PixCobranca(models.Model):
    """Cobrança PIX com QR Code gerado no Mercado Pago."""

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        APROVADO = 'aprovado', 'Aprovado'
        REJEITADO = 'rejeitado', 'Rejeitado'
        CANCELADO = 'cancelado', 'Cancelado'
        EXPIRADO = 'expirado', 'Expirado'
        ERRO = 'erro', 'Erro'

    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name='cobrancas_pix',
        verbose_name='máquina',
    )
    config = models.ForeignKey(
        MercadoPagoConfig,
        on_delete=models.PROTECT,
        related_name='cobrancas',
        verbose_name='conta MP',
        null=True,
        blank=True,
    )
    external_reference = models.UUIDField(
        'referência externa',
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    mp_payment_id = models.BigIntegerField(
        'ID pagamento MP',
        null=True,
        blank=True,
        db_index=True,
    )
    valor = models.DecimalField('valor (R$)', max_digits=10, decimal_places=2)
    creditos_concedidos = models.PositiveIntegerField(
        'créditos concedidos',
        null=True,
        blank=True,
        help_text='Quantidade definida na configuração no momento da cobrança.',
    )
    descricao = models.CharField('descrição', max_length=255, blank=True)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        db_index=True,
    )
    qr_code = models.TextField(
        'PIX copia e cola',
        blank=True,
        help_text='Código EMV para pagamento.',
    )
    qr_code_base64 = models.TextField('QR Code (base64)', blank=True)
    ticket_url = models.URLField('URL do comprovante', max_length=512, blank=True)
    expires_at = models.DateTimeField('expira em', null=True, blank=True)
    credito = models.OneToOneField(
        Credito,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cobranca_pix',
        verbose_name='crédito gerado',
    )
    ultimo_erro = models.TextField('último erro', blank=True)
    mp_status_detail = models.CharField('detalhe MP', max_length=64, blank=True)
    raw_response = models.JSONField('resposta MP', default=dict, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)
    approved_at = models.DateTimeField('aprovado em', null=True, blank=True)

    class Meta:
        verbose_name = 'cobrança PIX'
        verbose_name_plural = 'cobranças PIX'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['maquina', 'status'], name='pag_pix_maq_status_idx'),
            models.Index(fields=['created_at'], name='pag_pix_created_idx'),
        ]

    def __str__(self):
        return f'PIX R$ {self.valor} — {self.maquina} ({self.status})'
