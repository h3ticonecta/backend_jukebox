from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mercadopagoconfig',
            name='email_pagador_padrao',
            field=models.EmailField(
                default='gustavo.santos@h3ti.com.br',
                help_text='Obrigatório para a API do Mercado Pago (payer.email). Não use o usuário da jukebox.',
                max_length=254,
                verbose_name='e-mail padrão do pagador',
            ),
        ),
    ]
