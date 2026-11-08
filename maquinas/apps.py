from django.apps import AppConfig


class MaquinasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maquinas'
    verbose_name = 'Máquinas'

    def ready(self):
        import maquinas.signals  # noqa: F401
