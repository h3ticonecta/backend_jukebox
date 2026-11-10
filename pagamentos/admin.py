from django import forms
from django.contrib import admin
from django.forms.widgets import PasswordInput

from pagamentos.models import MercadoPagoConfig, PixCreditoOpcao, PixCobranca


class MercadoPagoConfigAdminForm(forms.ModelForm):
    access_token = forms.CharField(
        label='access token',
        widget=PasswordInput(render_value=True),
        help_text='Token de acesso da conta Mercado Pago (produção ou teste).',
    )

    class Meta:
        model = MercadoPagoConfig
        fields = '__all__'


@admin.register(MercadoPagoConfig)
class MercadoPagoConfigAdmin(admin.ModelAdmin):
    form = MercadoPagoConfigAdminForm
    list_display = ('nome', 'usar_sandbox', 'is_active', 'id_conta', 'updated_at')
    list_filter = ('is_active', 'usar_sandbox')
    search_fields = ('nome', 'id_conta', 'public_key')
    fieldsets = (
        (None, {
            'fields': ('nome', 'is_active', 'usar_sandbox'),
        }),
        ('Credenciais Mercado Pago', {
            'fields': ('access_token', 'public_key', 'id_conta'),
        }),
        ('Webhook', {
            'fields': ('webhook_url',),
            'description': (
                'Deixe em branco para usar https://<seu-backend>/api/v1/pagamentos/webhook/mercadopago/ '
                'Informe a mesma URL no painel do Mercado Pago (notificações IPN/Webhooks).'
            ),
        }),
        ('PIX', {
            'fields': ('email_pagador_padrao',),
            'description': 'E-mail técnico enviado como payer.email ao Mercado Pago (obrigatório e válido).',
        }),
    )


@admin.register(PixCreditoOpcao)
class PixCreditoOpcaoAdmin(admin.ModelAdmin):
    list_display = ('valor_pix', 'quantidade_creditos', 'ordem', 'ativo', 'updated_at')
    list_editable = ('quantidade_creditos', 'ordem', 'ativo')
    list_filter = ('ativo',)
    ordering = ('ordem', 'valor_pix')
    search_fields = ('valor_pix',)


@admin.register(PixCobranca)
class PixCobrancaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'maquina',
        'valor',
        'creditos_concedidos',
        'status',
        'mp_payment_id',
        'credito',
        'created_at',
        'approved_at',
    )
    list_filter = ('status', 'maquina', 'created_at')
    search_fields = ('maquina__nome_jukebox', 'qr_code', 'external_reference')
    readonly_fields = (
        'external_reference',
        'mp_payment_id',
        'qr_code',
        'qr_code_base64',
        'ticket_url',
        'credito',
        'raw_response',
        'created_at',
        'updated_at',
        'approved_at',
    )
    date_hierarchy = 'created_at'
