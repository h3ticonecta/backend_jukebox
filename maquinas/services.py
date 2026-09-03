from decimal import Decimal

from django.db.models import Count, Max, Sum
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date

from maquinas.models import Credito, MusicaTocada


def coerce_maquina_id(value):
    if not value:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def apply_period(queryset, inicio=None, fim=None, field='created_at'):
    if inicio:
        parsed = parse_date(str(inicio))
        if parsed:
            queryset = queryset.filter(**{f'{field}__date__gte': parsed})
    if fim:
        parsed = parse_date(str(fim))
        if parsed:
            queryset = queryset.filter(**{f'{field}__date__lte': parsed})
    return queryset


def money(value):
    if value is None:
        return '0.00'
    return f'{Decimal(value):.2f}'


def relatorio_faturamento(maquina_id=None, inicio=None, fim=None):
    maquina_id = coerce_maquina_id(maquina_id)
    creditos = Credito.objects.select_related('maquina')
    tocadas = MusicaTocada.objects.all()
    if maquina_id:
        creditos = creditos.filter(maquina_id=maquina_id)
        tocadas = tocadas.filter(maquina_id=maquina_id)
    creditos = apply_period(creditos, inicio, fim)
    tocadas = apply_period(tocadas, inicio, fim)

    total = creditos.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    por_origem = [
        {'origem': row['origem'], 'total': money(row['total']), 'quantidade': row['quantidade']}
        for row in creditos.values('origem').annotate(
            total=Sum('valor'),
            quantidade=Count('id'),
        ).order_by('-total')
    ]
    por_maquina = [
        {
            'maquina_id': row['maquina_id'],
            'nome_jukebox': row['maquina__nome_jukebox'],
            'total': money(row['total']),
            'quantidade': row['quantidade'],
        }
        for row in creditos.values('maquina_id', 'maquina__nome_jukebox').annotate(
            total=Sum('valor'),
            quantidade=Count('id'),
        ).order_by('-total')
    ]
    por_dia = [
        {
            'data': row['dia'].isoformat() if row['dia'] else None,
            'total': money(row['total']),
            'quantidade': row['quantidade'],
        }
        for row in creditos.annotate(dia=TruncDate('created_at')).values('dia').annotate(
            total=Sum('valor'),
            quantidade=Count('id'),
        ).order_by('dia')
    ]

    return {
        'inicio': inicio or None,
        'fim': fim or None,
        'maquina_id': int(maquina_id) if maquina_id else None,
        'faturamento_total': money(total),
        'creditos_quantidade': creditos.count(),
        'tocadas_quantidade': tocadas.count(),
        'por_origem': por_origem,
        'por_maquina': por_maquina,
        'por_dia': por_dia,
    }


def relatorio_mais_tocadas(maquina_id=None, inicio=None, fim=None, limit=20):
    maquina_id = coerce_maquina_id(maquina_id)
    queryset = MusicaTocada.objects.all()
    if maquina_id:
        queryset = queryset.filter(maquina_id=maquina_id)
    queryset = apply_period(queryset, inicio, fim)
    try:
        limit = max(1, min(int(limit or 20), 100))
    except (TypeError, ValueError):
        limit = 20

    ranking = list(
        queryset.values('musica_key').annotate(
            plays=Count('id'),
            musica_nome=Max('musica_nome'),
            titulo=Max('titulo'),
            pasta=Max('pasta'),
            media_type=Max('media_type'),
            cover_url=Max('cover_url'),
            media_url=Max('media_url'),
        ).order_by('-plays')[:limit]
    )

    return {
        'inicio': inicio or None,
        'fim': fim or None,
        'maquina_id': int(maquina_id) if maquina_id else None,
        'total_tocadas': queryset.count(),
        'ranking': ranking,
    }
