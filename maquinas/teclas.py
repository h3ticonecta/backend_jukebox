"""Atalhos de teclado da jukebox — valores padrão e validação."""

TECLAS_PADRAO = [
    {'acao': 'cima', 'label': 'Cima', 'tecla': 'Q'},
    {'acao': 'baixo', 'label': 'Baixo', 'tecla': 'W'},
    {'acao': 'esquerda', 'label': 'Esquerda', 'tecla': 'E'},
    {'acao': 'direita', 'label': 'Direita', 'tecla': 'R'},
    {'acao': 'credito', 'label': 'Crédito', 'tecla': 'K'},
    {'acao': 'hits', 'label': 'HITS', 'tecla': 'I'},
    {'acao': 'fila', 'label': 'Fila', 'tecla': 'F'},
    {'acao': 'pular', 'label': 'Pular', 'tecla': 'P'},
    {'acao': 'tocar_cd', 'label': 'Tocar CD', 'tecla': 'C'},
    {'acao': 'vol', 'label': 'Vol', 'tecla': 'V'},
    {'acao': 'cancelar', 'label': 'Cancelar', 'tecla': 'Enter'},
]

ACOES_VOLUME_LEGADAS = frozenset({'vol_mais', 'vol_menos'})

ACOES_VALIDAS = {item['acao'] for item in TECLAS_PADRAO}

ACAO_VOL = 'vol'

# Comportamento esperado no app (único botão físico de volume).
COMPORTAMENTO_VOL = {
    'modo': 'unico_botao',
    'clique_unico': 'aumentar',
    'cliques_repetidos': 'diminuir',
    'pressionar_segurar': 'diminuir_continuo',
}


def default_teclas():
    return [dict(item) for item in TECLAS_PADRAO]


def extrair_tecla_volume(por_acao):
    """Prefere `vol`; senão reaproveita Vol+ / Vol- já salvos."""
    vol = por_acao.get(ACAO_VOL, {})
    tecla = str(vol.get('tecla', '')).strip()
    if tecla:
        return tecla
    for legado in ('vol_mais', 'vol_menos'):
        item = por_acao.get(legado, {})
        tecla = str(item.get('tecla', '')).strip()
        if tecla:
            return tecla
    return ''


def normalizar_acao(acao):
    acao = (acao or '').strip()
    if acao in ACOES_VOLUME_LEGADAS:
        return ACAO_VOL
    return acao


def normalizar_teclas(raw):
    """Mescla JSON salvo com o layout padrão (label fixo, tecla configurável)."""
    if not raw:
        return default_teclas()

    por_acao = {}
    if isinstance(raw, dict):
        for acao, valor in raw.items():
            acao = normalizar_acao(acao)
            if isinstance(valor, str):
                por_acao.setdefault(acao, {})['tecla'] = valor
            elif isinstance(valor, dict):
                existente = por_acao.get(acao, {})
                existente.update(valor)
                por_acao[acao] = existente
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get('acao'):
                acao = normalizar_acao(item['acao'])
                existente = por_acao.get(acao, {})
                if item.get('tecla'):
                    existente['tecla'] = item['tecla']
                por_acao[acao] = existente

    if ACAO_VOL not in por_acao and ACOES_VOLUME_LEGADAS & set(por_acao.keys()):
        tecla = extrair_tecla_volume(por_acao)
        if tecla:
            por_acao[ACAO_VOL] = {'tecla': tecla}

    resultado = []
    for padrao in TECLAS_PADRAO:
        acao = padrao['acao']
        custom = por_acao.get(acao, {})
        if acao == ACAO_VOL and not custom.get('tecla'):
            tecla = extrair_tecla_volume(por_acao) or padrao['tecla']
        else:
            tecla = str(custom.get('tecla', padrao['tecla'])).strip() or padrao['tecla']
        resultado.append({
            'acao': acao,
            'label': padrao['label'],
            'tecla': tecla,
        })
    return resultado


def payload_teclas_config():
    """Metadados extras enviados ao app junto com as teclas."""
    return {
        'comportamento_volume': COMPORTAMENTO_VOL,
    }
