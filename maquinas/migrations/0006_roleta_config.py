import django.db.models.deletion
from decimal import Decimal

from django.db import migrations, models


def _seed_faixas_historicas(RoletaFaixaValor, RoletaPremioFaixa, config, faixas):
    for ordem, faixa in enumerate(faixas):
        row = RoletaFaixaValor.objects.create(
            config_id=config.pk,
            valor=Decimal(faixa['valor']),
            giros_liberados=faixa['giros_liberados'],
            ordem=ordem,
        )
        for p_ordem, premio in enumerate(faixa['premios']):
            RoletaPremioFaixa.objects.create(
                faixa_id=row.pk,
                tipo=premio['tipo'],
                quantidade=premio['quantidade'],
                peso=premio['peso'],
                ordem=p_ordem,
            )


def criar_roleta_maquinas_existentes(apps, schema_editor):
    """Usa modelos históricos — não chamar roleta_services na migração."""
    Maquina = apps.get_model('maquinas', 'Maquina')
    RoletaConfig = apps.get_model('maquinas', 'RoletaConfig')
    RoletaFaixaValor = apps.get_model('maquinas', 'RoletaFaixaValor')
    RoletaPremioFaixa = apps.get_model('maquinas', 'RoletaPremioFaixa')
    from maquinas.roleta_defaults import (
        DEFAULT_FAIXAS,
        DEFAULT_PROBABILIDADES,
        DEFAULT_REGRAS,
    )

    defaults = {**DEFAULT_PROBABILIDADES, **DEFAULT_REGRAS}
    for maquina in Maquina.objects.all().iterator():
        config, created = RoletaConfig.objects.get_or_create(
            maquina_id=maquina.pk,
            defaults=defaults,
        )
        if created:
            _seed_faixas_historicas(
                RoletaFaixaValor,
                RoletaPremioFaixa,
                config,
                DEFAULT_FAIXAS,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('maquinas', '0005_tecla_vol_unica'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoletaConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ativada', models.BooleanField(default=False, verbose_name='roleta ativada')),
                ('peso_premio_mais_2_musicas', models.PositiveIntegerField(default=1, verbose_name='+2 músicas grátis (peso)')),
                ('peso_premio_mais_1_musica', models.PositiveIntegerField(default=5, verbose_name='+1 música grátis (peso)')),
                ('peso_bonus_recarga_50pct', models.PositiveIntegerField(default=1, verbose_name='50% bônus recarga (peso)')),
                ('peso_tente_novamente', models.PositiveIntegerField(default=40, verbose_name='Tente novamente (peso)')),
                ('peso_nao_foi_dessa_vez', models.PositiveIntegerField(default=30, verbose_name='Não foi dessa vez (peso)')),
                ('creditos_minimos_girar', models.PositiveIntegerField(default=5, help_text='Quantidade de créditos comprados para liberar a roleta.', verbose_name='créditos mínimos para girar')),
                ('max_premio_mais_2_musicas_dia_percent', models.PositiveSmallIntegerField(default=10, help_text='Limite de sessões que podem ganhar +2 músicas (% do total diário).', verbose_name='máx. prêmios "+2 músicas" por dia (%)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('maquina', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='roleta_config', to='maquinas.maquina', verbose_name='máquina')),
            ],
            options={
                'verbose_name': 'configuração da roleta',
                'verbose_name_plural': 'configurações da roleta',
            },
        ),
        migrations.CreateModel(
            name='RoletaFaixaValor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='valor (R$)')),
                ('giros_liberados', models.PositiveIntegerField(default=1, verbose_name='giros liberados')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='ordem')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faixas', to='maquinas.roletaconfig', verbose_name='configuração')),
            ],
            options={
                'verbose_name': 'faixa de valor da roleta',
                'verbose_name_plural': 'faixas de valor da roleta',
                'ordering': ['ordem', 'valor'],
            },
        ),
        migrations.CreateModel(
            name='RoletaPremioFaixa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('musica_gratis', 'Música grátis'), ('giro_extra', 'Giro extra'), ('sem_premio', 'Sem prêmio')], default='musica_gratis', max_length=32, verbose_name='tipo')),
                ('quantidade', models.PositiveIntegerField(default=1, verbose_name='quantidade')),
                ('peso', models.PositiveIntegerField(default=10, verbose_name='peso')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='ordem')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('faixa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='premios', to='maquinas.roletafaixavalor', verbose_name='faixa')),
            ],
            options={
                'verbose_name': 'prêmio da faixa',
                'verbose_name_plural': 'prêmios da faixa',
                'ordering': ['ordem', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='roletafaixavalor',
            constraint=models.UniqueConstraint(fields=('config', 'valor'), name='uniq_roleta_faixa_config_valor'),
        ),
        migrations.RunPython(criar_roleta_maquinas_existentes, migrations.RunPython.noop),
    ]
