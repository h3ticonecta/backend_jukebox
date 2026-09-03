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
    {'acao': 'vol_mais', 'label': 'Vol+', 'tecla': 'PgUp'},
    {'acao': 'vol_menos', 'label': 'Vol-', 'tecla': 'PgDn'},
    {'acao': 'cancelar', 'label': 'Cancelar', 'tecla': 'Enter'},
]

ACOES_VALIDAS = {item['acao'] for item in TECLAS_PADRAO}


def default_teclas():
    return [dict(item) for item in TECLAS_PADRAO]


def normalizar_teclas(raw):
    """Mescla JSON salvo com o layout padrão (label fixo, tecla configurável)."""
    if not raw:
        return default_teclas()

    por_acao = {}
    if isinstance(raw, dict):
        for acao, valor in raw.items():
            if isinstance(valor, str):
                por_acao[acao] = {'tecla': valor}
            elif isinstance(valor, dict):
                por_acao[acao] = valor
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get('acao'):
                por_acao[item['acao']] = item

    resultado = []
    for padrao in TECLAS_PADRAO:
        acao = padrao['acao']
        custom = por_acao.get(acao, {})
        tecla = str(custom.get('tecla', padrao['tecla'])).strip() or padrao['tecla']
        resultado.append({
            'acao': acao,
            'label': padrao['label'],
            'tecla': tecla,
        })
    return resultado
