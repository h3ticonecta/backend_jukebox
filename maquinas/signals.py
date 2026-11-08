from django.db.models.signals import post_save
from django.dispatch import receiver

from maquinas.models import Maquina
from maquinas.roleta_services import get_or_create_roleta_config


@receiver(post_save, sender=Maquina)
def criar_config_roleta_maquina(sender, instance, created, **kwargs):
    if created:
        get_or_create_roleta_config(instance)
