"""Valores padrão da roleta por máquina (espelham o painel do admin SPA)."""

DEFAULT_PROBABILIDADES = {
    'peso_premio_mais_2_musicas': 1,
    'peso_premio_mais_1_musica': 5,
    'peso_bonus_recarga_50pct': 1,
    'peso_tente_novamente': 40,
    'peso_nao_foi_dessa_vez': 30,
}

DEFAULT_REGRAS = {
    'creditos_minimos_girar': 5,
    'max_premio_mais_2_musicas_dia_percent': 10,
}

DEFAULT_FAIXAS = (
    {
        'valor': '5.00',
        'giros_liberados': 1,
        'premios': [
            {'tipo': 'musica_gratis', 'quantidade': 2, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
        ],
    },
    {
        'valor': '10.00',
        'giros_liberados': 2,
        'premios': [
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
            {'tipo': 'musica_gratis', 'quantidade': 2, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
            {'tipo': 'musica_gratis', 'quantidade': 1, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
        ],
    },
    {
        'valor': '20.00',
        'giros_liberados': 4,
        'premios': [
            {'tipo': 'musica_gratis', 'quantidade': 2, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
        ],
    },
    {
        'valor': '50.00',
        'giros_liberados': 5,
        'premios': [
            {'tipo': 'musica_gratis', 'quantidade': 2, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
            {'tipo': 'musica_gratis', 'quantidade': 2, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
            {'tipo': 'musica_gratis', 'quantidade': 3, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
        ],
    },
    {
        'valor': '100.00',
        'giros_liberados': 5,
        'premios': [
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
            {'tipo': 'musica_gratis', 'quantidade': 3, 'peso': 10},
            {'tipo': 'sem_premio', 'quantidade': 1, 'peso': 10},
            {'tipo': 'musica_gratis', 'quantidade': 2, 'peso': 10},
            {'tipo': 'giro_extra', 'quantidade': 1, 'peso': 10},
        ],
    },
)
