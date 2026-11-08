from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Max, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.dateparse import parse_date

from maquinas.models import Credito, Maquina, MusicaTocada


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


def resolve_periodo(preset=None, inicio=None, fim=None):
    """Presets do painel admin: tudo | hoje | semana | mes (aliases aceitos)."""
    preset_raw = (preset or 'tudo').strip().lower()
    if inicio or fim:
        return preset_raw, inicio, fim

    today = timezone.localdate()
    if preset_raw in ('hoje', 'today'):
        d = today.isoformat()
        return 'hoje', d, d
    if preset_raw in ('semana', 'esta_semana', 'week'):
        start = today - timedelta(days=today.weekday())
        return 'semana', start.isoformat(), today.isoformat()
    if preset_raw in ('mes', 'este_mes', 'month'):
        return 'mes', today.replace(day=1).isoformat(), today.isoformat()
    return 'tudo', None, None


def normalizar_status_filtro(status):
    status = (status or 'todos').strip().lower()
    if status in ('ativo', 'ativa', 'active', 'true', '1'):
        return 'ativo'
    if status in ('inativo', 'inativa', 'inactive', 'false', '0'):
        return 'inativo'
    return 'todos'


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


def leitura_faturamento(maquina, data_inicio=None, data_fim=None):
    """Leitura de faturamento da jukebox autenticada (aliases para o app)."""
    base = relatorio_faturamento(
        maquina_id=maquina.id,
        inicio=data_inicio,
        fim=data_fim,
    )
    creditos = base['creditos_quantidade']
    faturamento = base['faturamento_total']
    tocadas = base['tocadas_quantidade']

    return {
        'maquina_id': maquina.id,
        'nome_jukebox': maquina.nome_jukebox,
        'data_inicio': data_inicio or base.get('inicio'),
        'data_fim': data_fim or base.get('fim'),
        'faturamento': faturamento,
        'faturamento_total': faturamento,
        'total_faturamento': faturamento,
        'valor': faturamento,
        'valor_total': faturamento,
        'creditos': creditos,
        'total_creditos': creditos,
        'creditos_inseridos': creditos,
        'creditos_quantidade': creditos,
        'transacoes': creditos,
        'total_transacoes': creditos,
        'count': creditos,
        'quantidade': creditos,
        'tocadas': tocadas,
        'tocadas_quantidade': tocadas,
        'por_origem': base['por_origem'],
        'por_dia': base['por_dia'],
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


def painel_administrativo(
    maquina_id=None,
    inicio=None,
    fim=None,
    periodo=None,
    status='todos',
):
    """
    Métricas do painel em jukebox.h3ti.com.br/#/admin
    (PostgreSQL: maquinas_maquina, maquinas_credito, maquinas_musicatocada).
    """
    periodo, inicio, fim = resolve_periodo(periodo, inicio, fim)
    maquina_id = coerce_maquina_id(maquina_id)
    status = normalizar_status_filtro(status)

    maquinas = Maquina.objects.all().order_by('nome_jukebox')
    if status == 'ativo':
        maquinas = maquinas.filter(is_active=True)
    elif status == 'inativo':
        maquinas = maquinas.filter(is_active=False)
    if maquina_id:
        maquinas = maquinas.filter(pk=maquina_id)

    maquinas_ativas = Maquina.objects.filter(is_active=True).count()

    creditos = Credito.objects.select_related('maquina')
    tocadas = MusicaTocada.objects.select_related('maquina')
    if maquina_id:
        creditos = creditos.filter(maquina_id=maquina_id)
        tocadas = tocadas.filter(maquina_id=maquina_id)
    elif status == 'ativo':
        creditos = creditos.filter(maquina__is_active=True)
        tocadas = tocadas.filter(maquina__is_active=True)
    elif status == 'inativo':
        creditos = creditos.filter(maquina__is_active=False)
        tocadas = tocadas.filter(maquina__is_active=False)

    creditos = apply_period(creditos, inicio, fim)
    tocadas = apply_period(tocadas, inicio, fim)

    total = creditos.aggregate(soma=Sum('valor'))['soma'] or Decimal('0')
    stats_por_maquina = {
        row['maquina_id']: {
            'total': row['total'] or Decimal('0'),
            'quantidade': row['quantidade'],
        }
        for row in creditos.values('maquina_id').annotate(
            total=Sum('valor'),
            quantidade=Count('id'),
        )
    }

    faturamento_por_maquina = []
    grafico = []
    for maquina in maquinas:
        stats = stats_por_maquina.get(
            maquina.id,
            {'total': Decimal('0'), 'quantidade': 0},
        )
        valor = stats['total']
        item = {
            'maquina_id': maquina.id,
            'nome_jukebox': maquina.nome_jukebox,
            'faturamento': money(valor),
            'faturamento_numero': float(valor),
            'creditos': stats['quantidade'],
            'is_active': maquina.is_active,
        }
        faturamento_por_maquina.append(item)
        grafico.append({
            'maquina_id': maquina.id,
            'nome_jukebox': maquina.nome_jukebox,
            'valor': float(valor),
        })

    faturamento_por_maquina.sort(key=lambda row: row['faturamento_numero'], reverse=True)
    grafico.sort(key=lambda row: row['valor'], reverse=True)

    maquinas_opcoes = [
        {
            'id': row['id'],
            'nome_jukebox': row['nome_jukebox'],
            'is_active': row['is_active'],
        }
        for row in Maquina.objects.order_by('nome_jukebox').values(
            'id',
            'nome_jukebox',
            'is_active',
        )
    ]

    return {
        'painel': 'administrativo',
        'periodo': {
            'preset': periodo,
            'data_inicio': inicio,
            'data_fim': fim,
        },
        'filtros': {
            'maquina_id': int(maquina_id) if maquina_id else None,
            'status': status,
        },
        'resumo': {
            'faturamento_total': money(total),
            'faturamento_total_numero': float(total),
            'creditos_vendidos': creditos.count(),
            'musicas_tocadas': tocadas.count(),
            'maquinas_ativas': maquinas_ativas,
        },
        'faturamento_por_maquina': faturamento_por_maquina,
        'grafico_faturamento_por_maquina': grafico,
        'maquinas_opcoes': maquinas_opcoes,
    }
