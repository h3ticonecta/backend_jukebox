import os
import re

from django.shortcuts import get_object_or_404

from buckets.exceptions import BucketServiceError
from buckets.models import BucketConfig
from buckets.services import S3BucketService
from musicas.models import ALLOWED_MEDIA_EXTENSIONS, AUDIO_EXTENSIONS, VIDEO_EXTENSIONS


MUSIC_FOLDER_NAMES = {'musicas', 'músicas', 'music', 'songs'}


def normalize_prefix(prefix):
    if not prefix:
        return ''
    return prefix if prefix.endswith('/') else f'{prefix}/'


def strip_bucket_from_prefix(prefix, bucket_name):
    current = normalize_prefix(prefix)
    name = (bucket_name or '').strip('/')
    if name and current.startswith(f'{name}/'):
        return current[len(name) + 1:]
    return current


def listing_has_content(listing, prefix):
    prefix = normalize_prefix(prefix)
    folders = listing.get('folders') or []
    objects = [
        item for item in listing.get('objects') or []
        if item.get('key') not in {prefix, prefix.rstrip('/')}
    ]
    return bool(folders or objects)


def resolve_music_root_prefix(bucket_config, service=None):
    cached = getattr(bucket_config, '_effective_music_root', None)
    if cached is not None:
        return cached

    service = service or S3BucketService(bucket_config)
    configured = normalize_prefix(bucket_config.music_root_prefix)
    candidates = []
    for candidate in (
        configured,
        strip_bucket_from_prefix(configured, bucket_config.bucket_name),
        'Musicas/',
    ):
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    for candidate in candidates:
        listing = service.list_objects(prefix=candidate, max_keys=50)
        if listing_has_content(listing, candidate):
            bucket_config._effective_music_root = candidate
            return candidate

    root_listing = service.list_objects(prefix='', max_keys=200)
    for folder in root_listing.get('folders') or []:
        name = folder_name_from_prefix(folder).lower()
        if name in MUSIC_FOLDER_NAMES:
            resolved = normalize_prefix(folder)
            bucket_config._effective_music_root = resolved
            return resolved

    resolved = candidates[0] if candidates else ''
    bucket_config._effective_music_root = resolved
    return resolved


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


def resolve_browse_prefix(requested_prefix, root_prefix, bucket_name=None):
    root = normalize_prefix(root_prefix)

    if not requested_prefix:
        return root

    candidates = [normalize_prefix(requested_prefix)]
    stripped = strip_bucket_from_prefix(requested_prefix, bucket_name)
    if stripped not in candidates:
        candidates.append(stripped)

    for current in candidates:
        if current.startswith(root):
            return current
    return root


def validate_key_in_root(key, root_prefix):
    root = normalize_prefix(root_prefix)
    if not key.startswith(root):
        raise BucketServiceError(
            'Operação fora da pasta permitida de músicas.',
            'INVALID_PATH',
        )
    return key


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


def build_breadcrumbs(current_prefix, root_prefix):
    root = normalize_prefix(root_prefix)
    current = normalize_prefix(current_prefix)
    breadcrumbs = [{
        'name': folder_name_from_prefix(root.rstrip('/')) or 'Raiz',
        'path': root,
    }]

    relative = current[len(root):].strip('/')
    if relative:
        path = root
        for part in relative.split('/'):
            path = f'{path}{part}/'
            breadcrumbs.append({'name': part, 'path': path})

    return breadcrumbs


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
    service = S3BucketService(bucket_config)
    root_prefix = resolve_music_root_prefix(bucket_config, service=service)
    current_prefix = resolve_browse_prefix(
        prefix,
        root_prefix,
        bucket_name=bucket_config.bucket_name,
    )

    all_objects = service.list_all_objects(prefix=root_prefix)
    all_keys = [item['key'] for item in all_objects]
    level = service.list_directory(current_prefix)

    folder_paths = set(extract_folder_paths(all_keys, root_prefix))
    for folder_path in level['folders']:
        folder_paths.add(normalize_prefix(folder_path))
    for item in level['objects']:
        key = item['key']
        if key.endswith('/') and key.startswith(root_prefix) and key != current_prefix:
            folder_paths.add(normalize_prefix(key))
    folder_paths = sorted(folder_paths, key=str.lower)
    tree = build_folder_tree(root_prefix, folder_paths)

    all_files = sorted(
        [
            build_media_item(item)
            for item in all_objects
            if is_media_key(item['key']) and not item['key'].endswith('/')
        ],
        key=lambda item: item['name'].lower(),
    )

    current_files = [
        item for item in all_files
        if item['folder_path'] == current_prefix
    ]

    current_folder_paths = [
        folder_path for folder_path in folder_paths
        if folder_path.startswith(current_prefix)
        and folder_path != current_prefix
        and folder_path[len(current_prefix):].strip('/').count('/') == 0
    ]
    current_folders = [
        {
            'name': folder_name_from_prefix(folder_path),
            'path': folder_path,
        }
        for folder_path in current_folder_paths
    ]

    return {
        'mode': 'file_manager',
        'bucket_id': bucket_config.id,
        'bucket_name': bucket_config.bucket_name,
        'root_path': root_prefix,
        'current_path': current_prefix,
        'parent_path': get_parent_path(current_prefix, root_prefix),
        'breadcrumbs': build_breadcrumbs(current_prefix, root_prefix),
        'tree': tree,
        'folders': current_folders,
        'files': current_files,
        'files_list': all_files,
        'musicas': current_files,
        'musicas_list': all_files,
        'totals': {
            'folders': len(folder_paths),
            'files': len(all_files),
            'current_folders': len(current_folders),
            'current_files': len(current_files),
            'audio': sum(1 for item in all_files if item['media_type'] == 'audio'),
            'video': sum(1 for item in all_files if item['media_type'] == 'video'),
        },
    }


def upload_file_to_folder(bucket_config, prefix, uploaded_file):
    from musicas.models import Musica

    root_prefix = resolve_music_root_prefix(bucket_config)
    current_prefix = resolve_browse_prefix(
        prefix,
        root_prefix,
        bucket_name=bucket_config.bucket_name,
    )

    Musica.validate_audio_extension(uploaded_file.name)
    safe_name = re.sub(r'[^\w.\-]', '_', uploaded_file.name)
    key = f'{current_prefix}{safe_name}'
    validate_key_in_root(key, root_prefix)

    service = S3BucketService(bucket_config)
    service.upload_object(
        key=key,
        file_obj=uploaded_file.file,
        content_type=uploaded_file.content_type,
    )

    return {
        'key': key,
        'name': safe_name,
        'folder_path': current_prefix,
        'media_url': bucket_config.get_public_url(key),
    }


def move_file(bucket_config, source_key, destination_key):
    root_prefix = resolve_music_root_prefix(bucket_config)
    validate_key_in_root(source_key, root_prefix)
    validate_key_in_root(destination_key, root_prefix)

    service = S3BucketService(bucket_config)
    return service.move_object(source_key, destination_key)


def delete_files(bucket_config, keys):
    root_prefix = resolve_music_root_prefix(bucket_config)
    for key in keys:
        validate_key_in_root(key, root_prefix)

    service = S3BucketService(bucket_config)
    return service.delete_objects(keys)


def create_folder(bucket_config, prefix, folder_name):
    root_prefix = resolve_music_root_prefix(bucket_config)
    current_prefix = resolve_browse_prefix(
        prefix,
        root_prefix,
        bucket_name=bucket_config.bucket_name,
    )
    safe_name = re.sub(r'[^\w.\-]', '_', folder_name.strip())
    folder_key = f'{current_prefix}{safe_name}/'
    validate_key_in_root(folder_key, root_prefix)

    service = S3BucketService(bucket_config)
    return service.create_folder(folder_key)
