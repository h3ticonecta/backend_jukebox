import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Maquina(models.Model):
    nome_jukebox = models.CharField('nome da jukebox', max_length=150)
    usuario = models.CharField('usuário', max_length=150, unique=True)
    senha = models.CharField('senha', max_length=128)
    api_token = models.CharField('token da máquina', max_length=64, unique=True, blank=True)
    is_active = models.BooleanField('ativo', default=True)
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
