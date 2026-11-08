import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from maquinas.teclas import default_teclas, normalizar_teclas


class Maquina(models.Model):
    nome_jukebox = models.CharField('nome da jukebox', max_length=150)
    usuario = models.CharField('usuário', max_length=150, unique=True)
    senha = models.CharField('senha', max_length=128)
    api_token = models.CharField('token da máquina', max_length=64, unique=True, blank=True)
    is_active = models.BooleanField('ativo', default=True)
    teclas = models.JSONField(
        'atalhos de teclado',
        default=default_teclas,
        blank=True,
        help_text='Mapa de teclas da jukebox (configurado no admin, enviado ao app).',
    )
    last_login_at = models.DateTimeField('último acesso', null=True, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'máquina'
        verbose_name_plural = 'máquinas'
        ordering = ['nome_jukebox']

    def __str__(self):
        return self.nome_jukebox

    def set_password(self, raw_password):
        self.senha = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.senha)

    def rotate_token(self):
        self.api_token = secrets.token_hex(20)

    def get_teclas(self):
        return normalizar_teclas(self.teclas)

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.rotate_token()
        super().save(*args, **kwargs)


class CreditoOrigem(models.TextChoices):
    MOEDA = 'moeda', 'Moeda'
    NOTA = 'nota', 'Nota'
    PIX = 'pix', 'Pix'
    CREDITO = 'credito', 'Crédito'
    OUTRO = 'outro', 'Outro'


class Credito(models.Model):
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name='creditos',
        verbose_name='máquina',
    )
    valor = models.DecimalField('valor (R$)', max_digits=10, decimal_places=2)
    origem = models.CharField(
        'origem',
        max_length=20,
        choices=CreditoOrigem.choices,
        default=CreditoOrigem.MOEDA,
    )
    observacao = models.CharField('observação', max_length=255, blank=True)
    created_at = models.DateTimeField('inserido em', auto_now_add=True)

    class Meta:
        verbose_name = 'crédito inserido'
        verbose_name_plural = 'créditos inseridos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['maquina', 'created_at'], name='maquinas_cred_maq_dt_idx'),
        ]

    def __str__(self):
        return f'{self.maquina} — R$ {self.valor}'


class MusicaTocada(models.Model):
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name='tocadas',
        verbose_name='máquina',
    )
    musica_key = models.CharField('chave da música', max_length=1024, db_index=True)
    musica_nome = models.CharField('nome do arquivo', max_length=512)
    titulo = models.CharField('título', max_length=512, blank=True)
    pasta = models.CharField('pasta', max_length=1024, blank=True)
    media_type = models.CharField('tipo', max_length=16, default='audio')
    media_url = models.CharField('URL', max_length=2048, blank=True)
    cover_url = models.CharField('capa', max_length=2048, blank=True)
    valor = models.DecimalField(
        'valor cobrado (R$)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Opcional — se a escolha gerou cobrança específica.',
    )
    created_at = models.DateTimeField('escolhida em', auto_now_add=True)

    class Meta:
        verbose_name = 'música tocada'
        verbose_name_plural = 'músicas tocadas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['maquina', 'created_at'], name='maquinas_toc_maq_dt_idx'),
            models.Index(fields=['musica_key'], name='maquinas_toc_key_idx'),
        ]

    def __str__(self):
        return f'{self.titulo or self.musica_nome} ({self.maquina})'


class RoletaConfig(models.Model):
    """Configuração da roleta — uma por máquina."""

    maquina = models.OneToOneField(
        Maquina,
        on_delete=models.CASCADE,
        related_name='roleta_config',
        verbose_name='máquina',
    )
    ativada = models.BooleanField('roleta ativada', default=False)
    peso_premio_mais_2_musicas = models.PositiveIntegerField(
        '+2 músicas grátis (peso)',
        default=1,
    )
    peso_premio_mais_1_musica = models.PositiveIntegerField(
        '+1 música grátis (peso)',
        default=5,
    )
    peso_bonus_recarga_50pct = models.PositiveIntegerField(
        '50% bônus recarga (peso)',
        default=1,
    )
    peso_tente_novamente = models.PositiveIntegerField(
        'Tente novamente (peso)',
        default=40,
    )
    peso_nao_foi_dessa_vez = models.PositiveIntegerField(
        'Não foi dessa vez (peso)',
        default=30,
    )
    creditos_minimos_girar = models.PositiveIntegerField(
        'créditos mínimos para girar',
        default=5,
        help_text='Quantidade de créditos comprados para liberar a roleta.',
    )
    max_premio_mais_2_musicas_dia_percent = models.PositiveSmallIntegerField(
        'máx. prêmios "+2 músicas" por dia (%)',
        default=10,
        help_text='Limite de sessões que podem ganhar +2 músicas (% do total diário).',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'configuração da roleta'
        verbose_name_plural = 'configurações da roleta'

    def __str__(self):
        return f'Roleta — {self.maquina.nome_jukebox}'

    @property
    def pesos_probabilidade(self):
        return (
            self.peso_premio_mais_2_musicas
            + self.peso_premio_mais_1_musica
            + self.peso_bonus_recarga_50pct
            + self.peso_tente_novamente
            + self.peso_nao_foi_dessa_vez
        )

    @property
    def pesos_usuario_ganha(self):
        return (
            self.peso_premio_mais_2_musicas
            + self.peso_premio_mais_1_musica
            + self.peso_bonus_recarga_50pct
        )


class RoletaFaixaValor(models.Model):
    """Faixa de valor inserido (ex.: R$ 5,00) com giros liberados."""

    config = models.ForeignKey(
        RoletaConfig,
        on_delete=models.CASCADE,
        related_name='faixas',
        verbose_name='configuração',
    )
    valor = models.DecimalField('valor (R$)', max_digits=10, decimal_places=2)
    giros_liberados = models.PositiveIntegerField('giros liberados', default=1)
    ordem = models.PositiveIntegerField('ordem', default=0)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'faixa de valor da roleta'
        verbose_name_plural = 'faixas de valor da roleta'
        ordering = ['ordem', 'valor']
        constraints = [
            models.UniqueConstraint(
                fields=['config', 'valor'],
                name='uniq_roleta_faixa_config_valor',
            ),
        ]

    def __str__(self):
        return f'R$ {self.valor} — {self.giros_liberados} giro(s)'


class RoletaPremioFaixa(models.Model):
    """Prêmio possível dentro de uma faixa de valor (roleta ponderada)."""

    class TipoPremio(models.TextChoices):
        MUSICA_GRATIS = 'musica_gratis', 'Música grátis'
        GIRO_EXTRA = 'giro_extra', 'Giro extra'
        SEM_PREMIO = 'sem_premio', 'Sem prêmio'

    faixa = models.ForeignKey(
        RoletaFaixaValor,
        on_delete=models.CASCADE,
        related_name='premios',
        verbose_name='faixa',
    )
    tipo = models.CharField(
        'tipo',
        max_length=32,
        choices=TipoPremio.choices,
        default=TipoPremio.MUSICA_GRATIS,
    )
    quantidade = models.PositiveIntegerField('quantidade', default=1)
    peso = models.PositiveIntegerField('peso', default=10)
    ordem = models.PositiveIntegerField('ordem', default=0)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'prêmio da faixa'
        verbose_name_plural = 'prêmios da faixa'
        ordering = ['ordem', 'id']

    def __str__(self):
        return f'{self.get_tipo_display()} × {self.quantidade} (peso {self.peso})'
