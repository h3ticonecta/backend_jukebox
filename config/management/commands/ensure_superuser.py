import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Cria ou atualiza o superusuário a partir das variáveis de ambiente.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        self.stdout.write(f'Banco em uso: {connection.vendor}')

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_USERNAME e DJANGO_SUPERUSER_PASSWORD não definidos. Pulando.',
                ),
            )
            return

        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()

        if user:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.password = make_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" atualizado.'))
            return

        user_model.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" criado.'))
