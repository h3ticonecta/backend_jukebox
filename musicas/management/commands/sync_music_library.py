from django.core.management.base import BaseCommand

from buckets.exceptions import BucketServiceError
from musicas.services import get_music_bucket, sync_music_library


class Command(BaseCommand):
    help = 'Sincroniza a biblioteca de músicas do R2 para o catálogo no PostgreSQL.'

    def handle(self, *args, **options):
        try:
            bucket = get_music_bucket()
            result = sync_music_library(bucket)
        except BucketServiceError as exc:
            self.stderr.write(self.style.ERROR(exc.message))
            return

        self.stdout.write(self.style.SUCCESS(
            'Biblioteca sincronizada: '
            f'{result["folders"]} pasta(s), '
            f'{result["files"]} faixa(s), '
            f'{result["images"]} capa(s).'
        ))
