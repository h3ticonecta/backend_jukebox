import os
import re

from django.db import models

from buckets.models import BucketConfig

ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}


def musica_upload_path(instance, filename):
  return f'musicas/{instance.pk or "temp"}/{filename}'


class Musica(models.Model):
    title = models.CharField('título', max_length=255)
    artist = models.CharField('artista', max_length=255, blank=True)
    album = models.CharField('álbum', max_length=255, blank=True)
    storage_key = models.CharField('chave no bucket', max_length=1024, blank=True)
    bucket = models.ForeignKey(
        BucketConfig,
        on_delete=models.PROTECT,
        related_name='musicas',
        verbose_name='bucket',
    )
    duration_seconds = models.PositiveIntegerField('duração (segundos)', null=True, blank=True)
    file_size = models.PositiveBigIntegerField('tamanho do arquivo', null=True, blank=True)
    content_type = models.CharField('tipo do arquivo', max_length=100, blank=True)
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'música'
        verbose_name_plural = 'músicas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.artist}' if self.artist else self.title

    @property
    def audio_url(self):
        if not self.storage_key:
            return None
        return self.bucket.get_public_url(self.storage_key)

    @staticmethod
    def validate_audio_extension(filename):
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_AUDIO_EXTENSIONS:
            allowed = ', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))
            raise ValueError(f'Extensão não permitida. Use: {allowed}')
        return extension

    @staticmethod
    def build_storage_key(musica_id, filename):
        safe_name = re.sub(r'[^\w.\-]', '_', filename)
        return f'musicas/{musica_id}/{safe_name}'
