from decimal import Decimal

from django.db import transaction

from maquinas.models import RoletaConfig, RoletaFaixaValor, RoletaPremioFaixa
from maquinas.roleta_defaults import (
    DEFAULT_FAIXAS,
    DEFAULT_PROBABILIDADES,
    DEFAULT_REGRAS,
)


def probabilidades_resumo(config):
    total = config.pesos_probabilidade
    ganha = config.pesos_usuario_ganha
    if total <= 0:
        return {
            'total_pesos': 0,
            'chance_usuario_ganhar_percent': 0.0,
            'vantagem_sistema_percent': 0.0,
        }
    chance = round(ganha * 100.0 / total, 1)
    return {
        'total_pesos': total,
        'chance_usuario_ganhar_percent': chance,
        'vantagem_sistema_percent': round(100.0 - chance, 1),
    }


def get_or_create_roleta_config(maquina):
    config, created = RoletaConfig.objects.get_or_create(
        maquina=maquina,
        defaults={
            **DEFAULT_PROBABILIDADES,
            **DEFAULT_REGRAS,
        },
    )
    if created:
        seed_faixas_padrao(config)
    return config


def seed_faixas_padrao(config):
    if config.faixas.exists():
        return
    for ordem, faixa in enumerate(DEFAULT_FAIXAS):
        row = RoletaFaixaValor.objects.create(
            config=config,
            valor=Decimal(faixa['valor']),
            giros_liberados=faixa['giros_liberados'],
            ordem=ordem,
        )
        for p_ordem, premio in enumerate(faixa['premios']):
            RoletaPremioFaixa.objects.create(
                faixa=row,
                tipo=premio['tipo'],
                quantidade=premio['quantidade'],
                peso=premio['peso'],
                ordem=p_ordem,
            )


def _premio_row(premio):
    return {
        'id': premio.id,
        'tipo': premio.tipo,
        'tipo_label': premio.get_tipo_display(),
        'quantidade': premio.quantidade,
        'peso': premio.peso,
        'ordem': premio.ordem,
    }


def _faixa_row(faixa):
    return {
        'id': faixa.id,
        'valor': f'{faixa.valor:.2f}',
        'valor_numero': float(faixa.valor),
        'giros_liberados': faixa.giros_liberados,
        'ordem': faixa.ordem,
        'premios': [_premio_row(p) for p in faixa.premios.all()],
    }


def roleta_config_payload(config):
    faixas = config.faixas.prefetch_related('premios').all()
    return {
        'maquina_id': config.maquina_id,
        'nome_jukebox': config.maquina.nome_jukebox,
        'ativada': config.ativada,
        'probabilidades': {
            'premio_mais_2_musicas': config.peso_premio_mais_2_musicas,
            'premio_mais_1_musica': config.peso_premio_mais_1_musica,
            'bonus_recarga_50pct': config.peso_bonus_recarga_50pct,
            'tente_novamente': config.peso_tente_novamente,
            'nao_foi_dessa_vez': config.peso_nao_foi_dessa_vez,
            'resumo': probabilidades_resumo(config),
        },
        'regras': {
            'creditos_minimos_girar': config.creditos_minimos_girar,
            'max_premio_mais_2_musicas_dia_percent': config.max_premio_mais_2_musicas_dia_percent,
        },
        'faixas_valor': [_faixa_row(f) for f in faixas],
        'updated_at': config.updated_at.isoformat() if config.updated_at else None,
    }


def _apply_probabilidades(config, data):
    if not data:
        return
    aliases = {
        'premio_mais_2_musicas': 'peso_premio_mais_2_musicas',
        'premio_mais_1_musica': 'peso_premio_mais_1_musica',
        'bonus_recarga_50pct': 'peso_bonus_recarga_50pct',
        'tente_novamente': 'peso_tente_novamente',
        'nao_foi_dessa_vez': 'peso_nao_foi_dessa_vez',
    }
    for key, field in aliases.items():
        if key in data and data[key] is not None:
            setattr(config, field, int(data[key]))


def _apply_regras(config, data):
    if not data:
        return
    if 'creditos_minimos_girar' in data and data['creditos_minimos_girar'] is not None:
        config.creditos_minimos_girar = int(data['creditos_minimos_girar'])
    if (
        'max_premio_mais_2_musicas_dia_percent' in data
        and data['max_premio_mais_2_musicas_dia_percent'] is not None
    ):
        config.max_premio_mais_2_musicas_dia_percent = int(
            data['max_premio_mais_2_musicas_dia_percent'],
        )


def _replace_faixas(config, faixas):
    if faixas is None:
        return
    with transaction.atomic():
        config.faixas.all().delete()
        for ordem, item in enumerate(faixas):
            valor = Decimal(str(item['valor']))
            row = RoletaFaixaValor.objects.create(
                config=config,
                valor=valor,
                giros_liberados=int(item.get('giros_liberados') or 1),
                ordem=int(item.get('ordem', ordem)),
            )
            for p_ordem, premio in enumerate(item.get('premios') or []):
                tipo = premio.get('tipo')
                if tipo not in RoletaPremioFaixa.TipoPremio.values:
                    raise ValueError(f'Tipo de prêmio inválido: {tipo}')
                RoletaPremioFaixa.objects.create(
                    faixa=row,
                    tipo=tipo,
                    quantidade=int(premio.get('quantidade') or 1),
                    peso=int(premio.get('peso') or 1),
                    ordem=int(premio.get('ordem', p_ordem)),
                )


def update_roleta_config(maquina, payload):
    config = get_or_create_roleta_config(maquina)

    if 'ativada' in payload:
        config.ativada = bool(payload['ativada'])

    _apply_probabilidades(config, payload.get('probabilidades'))
    _apply_regras(config, payload.get('regras'))
    config.save()

    if 'faixas_valor' in payload:
        _replace_faixas(config, payload['faixas_valor'])

    config.refresh_from_db()
    return config
