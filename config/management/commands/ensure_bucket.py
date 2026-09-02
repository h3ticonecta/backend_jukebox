import os

from django.core.management.base import BaseCommand
from django.db import connection

from buckets.models import BucketConfig, BucketProvider


class Command(BaseCommand):
    help = 'Cria ou atualiza a configuração do bucket a partir das variáveis de ambiente.'

    def handle(self, *args, **options):
        self.stdout.write(f'Banco em uso: {connection.vendor}')

        name = os.environ.get('BUCKET_CONFIG_NAME')
        endpoint_url = os.environ.get('BUCKET_ENDPOINT_URL')
        bucket_name = os.environ.get('BUCKET_NAME')
        access_key_id = os.environ.get('BUCKET_ACCESS_KEY_ID')
        secret_access_key = os.environ.get('BUCKET_SECRET_ACCESS_KEY')

        if not all([name, endpoint_url, bucket_name, access_key_id, secret_access_key]):
            self.stdout.write(
                self.style.WARNING(
                    'Variáveis de bucket incompletas. Pulando bootstrap do bucket.',
                ),
            )
            return

        provider = os.environ.get('BUCKET_PROVIDER', BucketProvider.CLOUDFLARE_R2)
        if provider not in BucketProvider.values:
            provider = BucketProvider.CLOUDFLARE_R2

        defaults = {
            'provider': provider,
            'endpoint_url': endpoint_url,
            'public_base_url': os.environ.get('BUCKET_PUBLIC_BASE_URL', ''),
            'bucket_name': bucket_name,
            'access_key_id': access_key_id,
            'secret_access_key': secret_access_key,
            'region_name': os.environ.get('BUCKET_REGION_NAME', 'auto'),
            'music_root_prefix': os.environ.get(
                'BUCKET_MUSIC_ROOT_PREFIX',
                'jukebox/Musicas/',
            ),
            'is_active': True,
        }

        bucket, created = BucketConfig.objects.update_or_create(
            name=name,
            defaults=defaults,
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Bucket "{name}" criado.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Bucket "{name}" atualizado.'))

        self.stdout.write(f'Bucket ID: {bucket.id} | Banco: {bucket.bucket_name}')
