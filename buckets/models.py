from django.db import models


class BucketProvider(models.TextChoices):
    AWS_S3 = 'aws_s3', 'AWS S3'
    CLOUDFLARE_R2 = 'cloudflare_r2', 'Cloudflare R2'


class BucketConfig(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    provider = models.CharField(
        'provedor',
        max_length=20,
        choices=BucketProvider.choices,
        default=BucketProvider.CLOUDFLARE_R2,
    )
    endpoint_url = models.URLField('URL do endpoint')
    public_base_url = models.URLField(
        'URL pública',
        blank=True,
        help_text='Ex: https://pub-xxxxx.r2.dev — usada para URLs públicas de arquivos',
    )
    music_root_prefix = models.CharField(
        'pasta raiz das músicas',
        max_length=1024,
        default='Musicas/',
        help_text='Prefixo das chaves no bucket, sem o nome do bucket. Ex: Musicas/',
    )
    bucket_name = models.CharField('nome do bucket', max_length=255)
    access_key_id = models.CharField('access key', max_length=255)
    secret_access_key = models.CharField('secret key', max_length=255)
    region_name = models.CharField('região', max_length=100, blank=True, default='auto')
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'configuração de bucket'
        verbose_name_plural = 'configurações de bucket'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.bucket_name})'

    def get_public_url(self, key):
        if not self.public_base_url or not key:
            return None
        base = self.public_base_url.rstrip('/')
        path = key.lstrip('/')
        return f'{base}/{path}'
