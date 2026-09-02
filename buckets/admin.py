from django.contrib import admin
from django.forms import PasswordInput

from buckets.models import BucketConfig


@admin.register(BucketConfig)
class BucketConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'provider',
        'bucket_name',
        'music_root_prefix',
        'is_active',
        'updated_at',
    )
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'bucket_name', 'endpoint_url', 'music_root_prefix')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'provider', 'is_active'),
            'description': 'Nome interno para identificar esta conexão no sistema.',
        }),
        ('Conexão R2 / S3', {
            'fields': (
                'endpoint_url',
                'bucket_name',
                'region_name',
            ),
            'description': (
                'Endpoint S3 para operações internas (upload, listagem, exclusão). '
                'Ex: https://ACCOUNT_ID.r2.cloudflarestorage.com'
            ),
        }),
        ('URLs públicas e biblioteca', {
            'fields': (
                'public_base_url',
                'music_root_prefix',
            ),
            'description': (
                'URL pública (pub-xxx.r2.dev) para o frontend tocar arquivos. '
                'Pasta raiz onde ficam as músicas no bucket.'
            ),
        }),
        ('Credenciais', {
            'fields': ('access_key_id', 'secret_access_key'),
            'description': 'Access Key e Secret Key do Cloudflare R2 ou AWS S3.',
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['secret_access_key'].widget = PasswordInput(render_value=True)
        return form
