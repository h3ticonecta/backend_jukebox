import os

from django.shortcuts import get_object_or_404

from buckets.exceptions import BucketServiceError
from buckets.models import BucketConfig
from buckets.services import S3BucketService
from musicas.models import ALLOWED_MEDIA_EXTENSIONS, AUDIO_EXTENSIONS, VIDEO_EXTENSIONS


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


def get_media_type(extension):
    if extension in VIDEO_EXTENSIONS:
        return 'video'
    if extension in AUDIO_EXTENSIONS:
        return 'audio'
    return 'other'


def is_media_key(key):
    extension = os.path.splitext(key)[1].lower()
    return extension in ALLOWED_MEDIA_EXTENSIONS


def build_media_item(item):
    key = item['key']
    filename = os.path.basename(key)
    title, extension = os.path.splitext(filename)
    folder_path = normalize_prefix('/'.join(key.split('/')[:-1]))

    return {
        'name': filename,
        'title': title,
        'key': key,
        'folder_path': folder_path,
        'extension': extension.lower(),
        'media_type': get_media_type(extension.lower()),
        'media_url': item.get('public_url'),
        'audio_url': item.get('public_url'),
        'size': item['size'],
        'last_modified': item['last_modified'],
    }


def extract_folder_paths(keys, root_prefix):
    root = normalize_prefix(root_prefix)
    folders = set()

    for key in keys:
        if key.endswith('/'):
            if key.startswith(root):
                folders.add(key)
            continue

        folder = normalize_prefix('/'.join(key.split('/')[:-1]))
        if not folder.startswith(root):
            continue

        relative = folder[len(root):].strip('/')
        if not relative:
            continue

        path = root
        for part in relative.split('/'):
            path = f'{path}{part}/'
            folders.add(path)

    return sorted(folders, key=str.lower)


def build_folder_tree(root_prefix, folder_paths):
    root = normalize_prefix(root_prefix)
    tree_map = {}

    for folder_path in folder_paths:
        relative = folder_path[len(root):].strip('/')
        if not relative:
            continue

        current = tree_map
        built_path = root
        for part in relative.split('/'):
            built_path = f'{built_path}{part}/'
            current = current.setdefault(part, {
                'name': part,
                'path': built_path,
                'children_map': {},
            })
            current = current['children_map']

    def map_to_list(nodes):
        children = []
        for name in sorted(nodes.keys(), key=str.lower):
            node = nodes[name]
            children.append({
                'name': node['name'],
                'path': node['path'],
                'children': map_to_list(node['children_map']),
            })
        return children

    return {
        'name': folder_name_from_prefix(root.rstrip('/')) or root,
        'path': root,
        'children': map_to_list(tree_map),
    }


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


def browse_music_library(bucket_config, prefix=None):
    root_prefix = normalize_prefix(bucket_config.music_root_prefix)
    current_prefix = resolve_browse_prefix(prefix, root_prefix)

    service = S3BucketService(bucket_config)
    all_objects = service.list_all_objects(prefix=root_prefix)
    all_keys = [item['key'] for item in all_objects]

    folder_paths = extract_folder_paths(all_keys, root_prefix)
    tree = build_folder_tree(root_prefix, folder_paths)

    all_musicas = sorted(
        [
            build_media_item(item)
            for item in all_objects
            if is_media_key(item['key']) and not item['key'].endswith('/')
        ],
        key=lambda item: item['name'].lower(),
    )

    current_musicas = [
        item for item in all_musicas
        if item['folder_path'] == current_prefix
    ]

    current_folders = [
        {
            'name': folder_name_from_prefix(folder_path),
            'path': folder_path,
        }
        for folder_path in folder_paths
        if folder_path.startswith(current_prefix)
        and folder_path != current_prefix
        and folder_path[len(current_prefix):].strip('/').count('/') == 0
    ]

    return {
        'bucket_id': bucket_config.id,
        'bucket_name': bucket_config.bucket_name,
        'root_path': root_prefix,
        'current_path': current_prefix,
        'parent_path': get_parent_path(current_prefix, root_prefix),
        'tree': tree,
        'folders': current_folders,
        'musicas': current_musicas,
        'musicas_list': all_musicas,
        'totals': {
            'folders': len(folder_paths),
            'musicas': len(all_musicas),
            'audio': sum(1 for item in all_musicas if item['media_type'] == 'audio'),
            'video': sum(1 for item in all_musicas if item['media_type'] == 'video'),
        },
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
