from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicas', '0002_bibliotecacatalogo_bibliotecaitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='musica',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'biblioteca de músicas',
                'verbose_name_plural': 'biblioteca de músicas',
            },
        ),
    ]
