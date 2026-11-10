import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('maquinas', '0006_roleta_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='MercadoPagoConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(default='Conta principal', help_text='Rótulo interno (ex.: conta produção H3TI).', max_length=120, verbose_name='identificação')),
                ('access_token', models.CharField(help_text='Token de produção ou teste do Mercado Pago.', max_length=512, verbose_name='access token')),
                ('public_key', models.CharField(blank=True, max_length=128, verbose_name='public key')),
                ('id_conta', models.CharField(blank=True, max_length=64, verbose_name='ID da conta MP')),
                ('usar_sandbox', models.BooleanField(default=False, verbose_name='modo teste (sandbox)')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
                ('webhook_url', models.URLField(blank=True, help_text='Opcional. Se vazio, usa a URL pública do backend + /api/v1/pagamentos/webhook/mercadopago/', max_length=512, verbose_name='URL de notificação (override)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'conta Mercado Pago',
                'verbose_name_plural': 'contas Mercado Pago',
                'ordering': ['-is_active', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='PixCobranca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_reference', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='referência externa')),
                ('mp_payment_id', models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name='ID pagamento MP')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='valor (R$)')),
                ('descricao', models.CharField(blank=True, max_length=255, verbose_name='descrição')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('aprovado', 'Aprovado'), ('rejeitado', 'Rejeitado'), ('cancelado', 'Cancelado'), ('expirado', 'Expirado'), ('erro', 'Erro')], db_index=True, default='pendente', max_length=20, verbose_name='status')),
                ('qr_code', models.TextField(blank=True, help_text='Código EMV para pagamento.', verbose_name='PIX copia e cola')),
                ('qr_code_base64', models.TextField(blank=True, verbose_name='QR Code (base64)')),
                ('ticket_url', models.URLField(blank=True, max_length=512, verbose_name='URL do comprovante')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expira em')),
                ('ultimo_erro', models.TextField(blank=True, verbose_name='último erro')),
                ('mp_status_detail', models.CharField(blank=True, max_length=64, verbose_name='detalhe MP')),
                ('raw_response', models.JSONField(blank=True, default=dict, verbose_name='resposta MP')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='aprovado em')),
                ('config', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cobrancas', to='pagamentos.mercadopagoconfig', verbose_name='conta MP')),
                ('credito', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cobranca_pix', to='maquinas.credito', verbose_name='crédito gerado')),
                ('maquina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cobrancas_pix', to='maquinas.maquina', verbose_name='máquina')),
            ],
            options={
                'verbose_name': 'cobrança PIX',
                'verbose_name_plural': 'cobranças PIX',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['maquina', 'status'], name='pag_pix_maq_status_idx'), models.Index(fields=['created_at'], name='pag_pix_created_idx')],
            },
        ),
    ]
