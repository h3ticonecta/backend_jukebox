from django.db import migrations


def unificar_tecla_volume(apps, schema_editor):
    Maquina = apps.get_model('maquinas', 'Maquina')
    from maquinas.teclas import normalizar_teclas

    for maquina in Maquina.objects.all().iterator():
        maquina.teclas = normalizar_teclas(maquina.teclas)
        maquina.save(update_fields=['teclas', 'updated_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('maquinas', '0004_tecla_tocar_cd'),
    ]

    operations = [
        migrations.RunPython(unificar_tecla_volume, migrations.RunPython.noop),
    ]
