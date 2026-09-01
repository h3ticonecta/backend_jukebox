from django.contrib import admin

from musicas.models import Musica


@admin.register(Musica)
class MusicaAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'bucket', 'is_active', 'created_at')
    list_filter = ('is_active', 'bucket')
    search_fields = ('title', 'artist', 'album', 'storage_key')
    readonly_fields = ('storage_key', 'audio_url', 'file_size', 'content_type', 'created_at', 'updated_at')

    fieldsets = (
        ('Música', {
            'fields': ('title', 'artist', 'album', 'duration_seconds', 'is_active'),
        }),
        ('Armazenamento', {
            'fields': ('bucket', 'storage_key', 'audio_url', 'file_size', 'content_type'),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
