import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria o superusuário a partir das variáveis de ambiente, se ainda não existir.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write('Variáveis de superusuário não definidas. Pulando.')
            return

        user_model = get_user_model()

        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f'Superusuário "{username}" já existe.')
            return

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" criado.'))
