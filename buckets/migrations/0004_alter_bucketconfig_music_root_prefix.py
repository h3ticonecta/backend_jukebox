from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buckets', '0003_bucketconfig_music_root_prefix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bucketconfig',
            name='music_root_prefix',
            field=models.CharField(
                default='Musicas/',
                help_text='Prefixo das chaves no bucket, sem o nome do bucket. Ex: Musicas/',
                max_length=1024,
                verbose_name='pasta raiz das músicas',
            ),
        ),
    ]
