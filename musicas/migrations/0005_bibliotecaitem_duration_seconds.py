from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicas', '0004_bibliotecaitem_cover_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='bibliotecaitem',
            name='duration_seconds',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Duração extraída do arquivo de áudio/vídeo no sync.',
                null=True,
                verbose_name='duração (segundos)',
            ),
        ),
    ]
