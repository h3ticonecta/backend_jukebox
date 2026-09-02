from urllib.parse import urlencode

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from buckets.exceptions import BucketServiceError
from musicas.models import Musica
from musicas.services import (
    browse_music_library,
    create_folder,
    delete_files,
    get_music_bucket,
    move_file,
    sync_music_library,
    upload_file_to_folder,
)


@admin.register(Musica)
class MusicaAdmin(admin.ModelAdmin):
    change_list_template = 'admin/musicas/file_manager.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'upload/',
                self.admin_site.admin_view(self.upload_view),
                name='musicas_musica_upload',
            ),
            path(
                'delete/',
                self.admin_site.admin_view(self.delete_view),
                name='musicas_musica_delete',
            ),
            path(
                'move/',
                self.admin_site.admin_view(self.move_view),
                name='musicas_musica_move',
            ),
            path(
                'create-folder/',
                self.admin_site.admin_view(self.create_folder_view),
                name='musicas_musica_create_folder',
            ),
            path(
                'sync/',
                self.admin_site.admin_view(self.sync_view),
                name='musicas_musica_sync',
            ),
        ]
        return custom_urls + urls

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        prefix = request.GET.get('prefix', '')
        search = request.GET.get('q', '').strip()
        context = {
            **self.admin_site.each_context(request),
            'title': 'Biblioteca de Músicas',
            'opts': self.model._meta,
            'has_view_permission': True,
            'cl': None,
            'error': None,
            'browse': None,
        }

        try:
            bucket = get_music_bucket()
            context['browse'] = browse_music_library(
                bucket,
                prefix=prefix,
                search=search,
            )
        except BucketServiceError as exc:
            context['error'] = exc.message

        if extra_context:
            context.update(extra_context)

        return TemplateResponse(request, self.change_list_template, context)

    def upload_view(self, request):
        if request.method != 'POST':
            return redirect('admin:musicas_musica_changelist')

        prefix = request.POST.get('prefix', '')
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            messages.error(request, 'Selecione um arquivo para enviar.')
            return self._redirect_prefix(prefix)

        try:
            bucket = get_music_bucket()
            upload_file_to_folder(bucket, prefix=prefix, uploaded_file=uploaded_file)
            messages.success(request, f'Arquivo "{uploaded_file.name}" enviado com sucesso.')
        except (BucketServiceError, ValueError) as exc:
            message = exc.message if hasattr(exc, 'message') else str(exc)
            messages.error(request, message)

        return self._redirect_prefix(prefix)

    def delete_view(self, request):
        if request.method != 'POST':
            return redirect('admin:musicas_musica_changelist')

        prefix = request.POST.get('prefix', '')
        keys = request.POST.getlist('keys')

        if not keys:
            messages.error(request, 'Selecione ao menos um arquivo para excluir.')
            return self._redirect_prefix(prefix)

        try:
            bucket = get_music_bucket()
            result = delete_files(bucket, keys=keys)
            messages.success(request, f'{len(result["deleted"])} arquivo(s) excluído(s).')
        except BucketServiceError as exc:
            messages.error(request, exc.message)

        return self._redirect_prefix(prefix)

    def move_view(self, request):
        if request.method != 'POST':
            return redirect('admin:musicas_musica_changelist')

        prefix = request.POST.get('prefix', '')
        source_key = request.POST.get('source_key', '')
        destination_key = request.POST.get('destination_key', '')

        try:
            bucket = get_music_bucket()
            move_file(bucket, source_key=source_key, destination_key=destination_key)
            messages.success(request, 'Arquivo movido com sucesso.')
        except BucketServiceError as exc:
            messages.error(request, exc.message)

        return self._redirect_prefix(prefix)

    def create_folder_view(self, request):
        if request.method != 'POST':
            return redirect('admin:musicas_musica_changelist')

        prefix = request.POST.get('prefix', '')
        folder_name = request.POST.get('name', '').strip()

        if not folder_name:
            messages.error(request, 'Informe o nome da pasta.')
            return self._redirect_prefix(prefix)

        try:
            bucket = get_music_bucket()
            create_folder(bucket, prefix=prefix, folder_name=folder_name)
            messages.success(request, f'Pasta "{folder_name}" criada com sucesso.')
        except BucketServiceError as exc:
            messages.error(request, exc.message)

        return self._redirect_prefix(prefix)

    def sync_view(self, request):
        if request.method != 'POST':
            return redirect('admin:musicas_musica_changelist')

        prefix = request.POST.get('prefix', '')
        try:
            bucket = get_music_bucket()
            result = sync_music_library(bucket)
            messages.success(
                request,
                (
                    'Biblioteca sincronizada: '
                    f'{result["folders"]} pasta(s), '
                    f'{result["files"]} faixa(s), '
                    f'{result["images"]} capa(s).'
                ),
            )
        except BucketServiceError as exc:
            messages.error(request, exc.message)

        return self._redirect_prefix(prefix)

    def _redirect_prefix(self, prefix):
        url = reverse('admin:musicas_musica_changelist')
        if prefix:
            url = f'{url}?{urlencode({"prefix": prefix})}'
        return redirect(url)
