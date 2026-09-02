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
