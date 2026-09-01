from django.contrib import admin
from django.forms import PasswordInput

from buckets.models import BucketConfig


@admin.register(BucketConfig)
class BucketConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'bucket_name', 'endpoint_url', 'is_active', 'updated_at')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'bucket_name', 'endpoint_url')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'provider', 'is_active'),
        }),
        ('Conexão', {
            'fields': ('endpoint_url', 'bucket_name', 'region_name'),
        }),
        ('Credenciais', {
            'fields': ('access_key_id', 'secret_access_key'),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['secret_access_key'].widget = PasswordInput(render_value=True)
        return form
