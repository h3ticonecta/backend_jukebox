import os

from django.shortcuts import get_object_or_404

from buckets.exceptions import BucketServiceError
from buckets.models import BucketConfig
from buckets.services import S3BucketService
from musicas.models import ALLOWED_AUDIO_EXTENSIONS


def normalize_prefix(prefix):
    if not prefix:
        return ''
    return prefix if prefix.endswith('/') else f'{prefix}/'


def folder_name_from_prefix(prefix):
    return prefix.rstrip('/').split('/')[-1]


def get_parent_path(current_prefix, root_prefix):
    current = normalize_prefix(current_prefix)
    root = normalize_prefix(root_prefix)

    if current == root:
        return None

    parent = '/'.join(current.rstrip('/').split('/')[:-1]) + '/'
    if len(parent) < len(root):
        return root
    return parent


def resolve_browse_prefix(requested_prefix, root_prefix):
    root = normalize_prefix(root_prefix)

    if not requested_prefix:
        return root

    current = normalize_prefix(requested_prefix)
    if not current.startswith(root):
        return root
    return current


def is_audio_key(key):
    extension = os.path.splitext(key)[1].lower()
    return extension in ALLOWED_AUDIO_EXTENSIONS


def get_music_bucket(bucket_id=None):
    if bucket_id:
        return get_object_or_404(BucketConfig, pk=bucket_id, is_active=True)

    bucket = BucketConfig.objects.filter(is_active=True, bucket_name='jukebox').first()
    if bucket is None:
        bucket = BucketConfig.objects.filter(is_active=True).first()
    if bucket is None:
        raise BucketServiceError(
            'Nenhum bucket ativo configurado.',
            'BUCKET_NOT_FOUND',
        )
    return bucket


def browse_music_library(bucket_config, prefix=None, continuation_token=None, max_keys=100):
    root_prefix = normalize_prefix(bucket_config.music_root_prefix)
    current_prefix = resolve_browse_prefix(prefix, root_prefix)

    service = S3BucketService(bucket_config)
    listing = service.list_objects(
        prefix=current_prefix,
        continuation_token=continuation_token,
        max_keys=max_keys,
    )

    folders = [
        {
            'name': folder_name_from_prefix(folder_prefix),
            'path': folder_prefix,
        }
        for folder_prefix in sorted(listing['folders'], key=lambda value: value.lower())
    ]

    musicas = []
    for item in listing['objects']:
        key = item['key']
        if key == current_prefix.rstrip('/') or key.endswith('/'):
            continue
        if not is_audio_key(key):
            continue

        filename = os.path.basename(key)
        title, _ = os.path.splitext(filename)
        musicas.append({
            'name': filename,
            'title': title,
            'key': key,
            'audio_url': item.get('public_url'),
            'size': item['size'],
            'last_modified': item['last_modified'],
        })

    musicas.sort(key=lambda item: item['name'].lower())

    return {
        'bucket_id': bucket_config.id,
        'bucket_name': bucket_config.bucket_name,
        'root_path': root_prefix,
        'current_path': current_prefix,
        'parent_path': get_parent_path(current_prefix, root_prefix),
        'folders': folders,
        'musicas': musicas,
        'is_truncated': listing['is_truncated'],
        'next_continuation_token': listing['next_continuation_token'],
    }


def upload_musica_file(musica, uploaded_file):
    from musicas.models import Musica

    Musica.validate_audio_extension(uploaded_file.name)

    storage_key = Musica.build_storage_key(musica.pk, uploaded_file.name)
    service = S3BucketService(musica.bucket)

    try:
        service.upload_object(
            key=storage_key,
            file_obj=uploaded_file.file,
            content_type=uploaded_file.content_type,
        )
    except BucketServiceError:
        raise

    musica.storage_key = storage_key
    musica.file_size = uploaded_file.size
    musica.content_type = uploaded_file.content_type or ''
    musica.save(update_fields=['storage_key', 'file_size', 'content_type', 'updated_at'])
    return musica


def delete_musica_file(musica):
    if not musica.storage_key:
        return

    service = S3BucketService(musica.bucket)
    try:
        service.delete_objects([musica.storage_key])
    except BucketServiceError:
        raise
