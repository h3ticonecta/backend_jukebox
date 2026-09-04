import os
import re

from django.db import models

from buckets.models import BucketConfig

AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
VIDEO_EXTENSIONS = {'.mp4'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

ALLOWED_MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS
ALLOWED_LIBRARY_EXTENSIONS = ALLOWED_MEDIA_EXTENSIONS | IMAGE_EXTENSIONS

# Compatibilidade com código existente
ALLOWED_AUDIO_EXTENSIONS = ALLOWED_LIBRARY_EXTENSIONS


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
        verbose_name = 'biblioteca de músicas'
        verbose_name_plural = 'biblioteca de músicas'
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
        if extension not in ALLOWED_LIBRARY_EXTENSIONS:
            allowed = ', '.join(sorted(ALLOWED_LIBRARY_EXTENSIONS))
            raise ValueError(f'Extensão não permitida. Use: {allowed}')
        return extension

    @staticmethod
    def build_storage_key(musica_id, filename):
        safe_name = re.sub(r'[^\w.\-]', '_', filename)
        return f'musicas/{musica_id}/{safe_name}'


class BibliotecaCatalogo(models.Model):
    bucket = models.OneToOneField(
        BucketConfig,
        on_delete=models.CASCADE,
        related_name='catalogo_musicas',
        verbose_name='bucket',
    )
    root_path = models.CharField('pasta raiz', max_length=1024, blank=True)
    last_synced_at = models.DateTimeField('sincronizado em', null=True, blank=True)
    is_syncing = models.BooleanField('sincronizando', default=False)
    last_error = models.TextField('último erro', blank=True)
    folders_count = models.PositiveIntegerField('pastas', default=0)
    files_count = models.PositiveIntegerField('arquivos', default=0)
    images_count = models.PositiveIntegerField('imagens', default=0)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'catálogo da biblioteca'
        verbose_name_plural = 'catálogos da biblioteca'

    def __str__(self):
        return f'Catálogo {self.bucket}'


class BibliotecaItem(models.Model):
    KIND_FILE = 'file'
    KIND_FOLDER = 'folder'
    KIND_CHOICES = (
        (KIND_FILE, 'arquivo'),
        (KIND_FOLDER, 'pasta'),
    )

    bucket = models.ForeignKey(
        BucketConfig,
        on_delete=models.CASCADE,
        related_name='biblioteca_itens',
        verbose_name='bucket',
    )
    kind = models.CharField('tipo', max_length=16, choices=KIND_CHOICES, db_index=True)
    key = models.CharField('chave', max_length=1024)
    name = models.CharField('nome', max_length=512)
    title = models.CharField('título', max_length=512, blank=True)
    folder_path = models.CharField('pasta', max_length=1024, db_index=True)
    extension = models.CharField('extensão', max_length=16, blank=True)
    media_type = models.CharField('tipo de mídia', max_length=16, db_index=True)
    size = models.PositiveBigIntegerField('tamanho', default=0)
    last_modified = models.CharField('modificado em', max_length=64, blank=True)
    media_url = models.CharField('URL pública', max_length=2048, blank=True)
    duration_seconds = models.PositiveIntegerField(
        'duração (segundos)',
        null=True,
        blank=True,
        help_text='Duração extraída do arquivo de áudio/vídeo no sync.',
    )
    cover_key = models.CharField(
        'chave da capa',
        max_length=1024,
        blank=True,
        help_text='Imagem usada como capa da pasta (própria ou herdada do primeiro filho).',
    )

    class Meta:
        verbose_name = 'item da biblioteca'
        verbose_name_plural = 'itens da biblioteca'
        constraints = [
            models.UniqueConstraint(
                fields=['bucket', 'key'],
                name='uniq_biblioteca_item_bucket_key',
            ),
        ]
        indexes = [
            models.Index(fields=['bucket', 'kind', 'folder_path'], name='musicas_biblio_path_idx'),
            models.Index(fields=['bucket', 'media_type'], name='musicas_biblio_media_idx'),
            models.Index(fields=['name'], name='musicas_biblio_name_idx'),
        ]
        ordering = ['name']

    def __str__(self):
        return self.key
