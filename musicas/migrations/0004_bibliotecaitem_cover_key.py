from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicas', '0003_alter_musica_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='bibliotecaitem',
            name='cover_key',
            field=models.CharField(
                blank=True,
                help_text='Imagem usada como capa da pasta (própria ou herdada do primeiro filho).',
                max_length=1024,
                verbose_name='chave da capa',
            ),
        ),
    ]
