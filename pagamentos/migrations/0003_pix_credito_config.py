from decimal import Decimal

from django.db import migrations, models


def criar_opcoes_padrao(apps, schema_editor):
    PixCreditoOpcao = apps.get_model('pagamentos', 'PixCreditoOpcao')
    padrao = (
        (Decimal('5.00'), 5, 1),
        (Decimal('10.00'), 10, 2),
        (Decimal('20.00'), 20, 3),
        (Decimal('50.00'), 50, 4),
        (Decimal('100.00'), 100, 5),
    )
    for valor, creditos, ordem in padrao:
        PixCreditoOpcao.objects.get_or_create(
            valor_pix=valor,
            defaults={
                'quantidade_creditos': creditos,
                'ordem': ordem,
                'ativo': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentos', '0002_mercadopagoconfig_email_pagador'),
    ]

    operations = [
        migrations.CreateModel(
            name='PixCreditoOpcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_pix', models.DecimalField(decimal_places=2, max_digits=10, unique=True, verbose_name='valor PIX (R$)')),
                ('quantidade_creditos', models.PositiveIntegerField(help_text='Créditos inseridos na máquina quando o PIX deste valor for aprovado.', verbose_name='quantidade de créditos')),
                ('ordem', models.PositiveSmallIntegerField(default=0, verbose_name='ordem')),
                ('ativo', models.BooleanField(default=True, verbose_name='ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'configuração créditos',
                'verbose_name_plural': 'créditos (configuração)',
                'ordering': ['ordem', 'valor_pix'],
            },
        ),
        migrations.AddField(
            model_name='pixcobranca',
            name='creditos_concedidos',
            field=models.PositiveIntegerField(blank=True, help_text='Quantidade definida na configuração no momento da cobrança.', null=True, verbose_name='créditos concedidos'),
        ),
        migrations.RunPython(criar_opcoes_padrao, migrations.RunPython.noop),
    ]
