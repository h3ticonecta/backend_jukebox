import os
import re

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from buckets.exceptions import BucketServiceError
from buckets.models import BucketConfig
from buckets.services import S3BucketService
from musicas.models import (
    ALLOWED_LIBRARY_EXTENSIONS,
    ALLOWED_MEDIA_EXTENSIONS,
    AUDIO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    BibliotecaCatalogo,
    BibliotecaItem,
    Musica,
)

COVER_FILENAMES = ('cover', 'folder', 'album', 'artwork', 'front', 'capa')


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
    if extension in IMAGE_EXTENSIONS:
        return 'image'
    return 'other'


def is_media_key(key):
    extension = os.path.splitext(key)[1].lower()
    return extension in ALLOWED_MEDIA_EXTENSIONS


def is_library_key(key):
    extension = os.path.splitext(key)[1].lower()
    return extension in ALLOWED_LIBRARY_EXTENSIONS


def pick_folder_cover(images):
    if not images:
        return None

    by_stem = {}
    for image in images:
        stem = image['title'].lower()
        by_stem.setdefault(stem, image)

    for name in COVER_FILENAMES:
        if name in by_stem:
            return by_stem[name]

    return sorted(images, key=lambda item: item['name'].lower())[0]


def get_direct_child_folders(folder_path, folder_paths):
    folder_path = normalize_prefix(folder_path)
    children = [
        path for path in folder_paths
        if path != folder_path
        and path.startswith(folder_path)
        and path[len(folder_path):].strip('/').count('/') == 0
    ]
    return sorted(children, key=lambda path: folder_name_from_prefix(path).lower())


def resolve_all_folder_covers(folder_paths, all_items):
    """Calcula capa de cada pasta: direta na pasta ou herdada do primeiro filho com capa."""
    folder_paths = sorted({normalize_prefix(path) for path in folder_paths if path}, key=str.lower)
    images_by_folder = {}
    for item in all_items:
        if item.get('media_type') == 'image':
            images_by_folder.setdefault(item['folder_path'], []).append(item)

    direct_covers = {}
    for folder_path in folder_paths:
        images = images_by_folder.get(folder_path, [])
        if images:
            cover = pick_folder_cover(images)
            if cover:
                direct_covers[folder_path] = cover

    resolved = {}
    for folder_path in sorted(folder_paths, key=lambda path: path.count('/'), reverse=True):
        if folder_path in direct_covers:
            resolved[folder_path] = direct_covers[folder_path]
            continue
        for child_path in get_direct_child_folders(folder_path, folder_paths):
            child_cover = resolved.get(child_path)
            if child_cover:
                resolved[folder_path] = child_cover
                break

    return resolved


def load_folder_covers_from_db(bucket_config):
    covers = {}
    rows = BibliotecaItem.objects.filter(
        bucket=bucket_config,
        kind=BibliotecaItem.KIND_FOLDER,
    ).exclude(media_url='')
    for row in rows:
        cover_key = row.cover_key or ''
        covers[row.key] = {
            'name': os.path.basename(cover_key) if cover_key else row.name,
            'key': cover_key,
            'media_url': row.media_url,
        }
    return covers


def rebuild_folder_covers(bucket_config):
    if not catalog_is_ready(bucket_config):
        return

    folder_paths = list(
        BibliotecaItem.objects.filter(
            bucket=bucket_config,
            kind=BibliotecaItem.KIND_FOLDER,
        ).values_list('key', flat=True),
    )
    file_rows = BibliotecaItem.objects.filter(
        bucket=bucket_config,
        kind=BibliotecaItem.KIND_FILE,
    )
    all_items = [item_from_model(row) for row in file_rows]
    folder_covers = resolve_all_folder_covers(folder_paths, all_items)

    folders = list(
        BibliotecaItem.objects.filter(
            bucket=bucket_config,
            kind=BibliotecaItem.KIND_FOLDER,
        ),
    )
    for folder in folders:
        cover = folder_covers.get(folder.key)
        if cover:
            folder.media_url = (cover.get('media_url') or '')[:2048]
            folder.cover_key = (cover.get('key') or '')[:1024]
        else:
            folder.media_url = ''
            folder.cover_key = ''

    if folders:
        BibliotecaItem.objects.bulk_update(
            folders,
            ['media_url', 'cover_key'],
            batch_size=500,
        )


def cover_payload(cover):
    if not cover:
        return None, None
    payload = {
        'name': cover['name'],
        'key': cover['key'],
        'media_url': cover.get('media_url'),
    }
    return cover.get('media_url'), payload


def build_media_item(item):
    key = item['key']
    filename = os.path.basename(key)
    title, extension = os.path.splitext(filename)
    folder_path = normalize_prefix('/'.join(key.split('/')[:-1]))
    media_type = get_media_type(extension.lower())
    public_url = item.get('public_url')

    return {
        'name': filename,
        'title': title,
        'key': key,
        'folder_path': folder_path,
        'extension': extension.lower(),
        'media_type': media_type,
        'media_url': public_url,
        'audio_url': public_url if media_type != 'image' else None,
        'cover_url': public_url if media_type == 'image' else None,
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


def build_folder_tree(root_prefix, folder_paths, covers_by_folder=None, folder_counts=None):
    root = normalize_prefix(root_prefix)
    covers_by_folder = covers_by_folder or {}
    folder_counts = folder_counts or {}
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
            counts = folder_counts.get(node['path'], {})
            children.append({
                'name': node['name'],
                'path': node['path'],
                'cover_url': covers_by_folder.get(node['path']),
                'subfolders_count': counts.get('subfolders', 0),
                'files_count': counts.get('files', 0),
                'children': map_to_list(node['children_map']),
            })
        return children

    return {
        'name': folder_name_from_prefix(root.rstrip('/')) or root,
        'path': root,
        'cover_url': covers_by_folder.get(root),
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


def configured_root_prefix(bucket_config):
    configured = normalize_prefix(bucket_config.music_root_prefix)
    stripped = strip_bucket_from_prefix(configured, bucket_config.bucket_name)
    return stripped or configured or 'Musicas/'


def get_catalog(bucket_config):
    return BibliotecaCatalogo.objects.filter(bucket=bucket_config).first()


def catalog_is_ready(bucket_config):
    catalog = get_catalog(bucket_config)
    return bool(catalog and catalog.last_synced_at)


def effective_root_prefix(bucket_config, probe_r2=False):
    catalog = get_catalog(bucket_config)
    if catalog and catalog.root_path:
        return catalog.root_path
    if probe_r2:
        return resolve_music_root_prefix(bucket_config)
    return configured_root_prefix(bucket_config)


def item_from_model(row):
    public_url = row.media_url or None
    return {
        'name': row.name,
        'title': row.title,
        'key': row.key,
        'folder_path': row.folder_path,
        'extension': row.extension,
        'media_type': row.media_type,
        'media_url': public_url,
        'audio_url': public_url if row.media_type != 'image' else None,
        'cover_url': public_url if row.media_type == 'image' else None,
        'size': row.size,
        'last_modified': row.last_modified,
    }


def assemble_browse(
    bucket_config,
    root_prefix,
    current_prefix,
    folder_paths,
    all_items,
    catalog=None,
    search=None,
    folder_covers_db=None,
):
    folder_paths = sorted({normalize_prefix(path) for path in folder_paths if path}, key=str.lower)
    all_items = sorted(all_items, key=lambda item: item['name'].lower())
    playable = [item for item in all_items if item['media_type'] in {'audio', 'video'}]
    all_images = [item for item in all_items if item['media_type'] == 'image']
    listed_files = sorted(playable + all_images, key=lambda item: item['name'].lower())

    if search:
        term = search.strip().lower()
        if term:
            listed_files = [
                item for item in listed_files
                if term in item['name'].lower() or term in item['key'].lower()
            ]

    images_by_folder = {}
    for image in all_images:
        images_by_folder.setdefault(image['folder_path'], []).append(image)

    if folder_covers_db:
        covers = folder_covers_db
        cover_urls = {
            path: cover.get('media_url')
            for path, cover in folder_covers_db.items()
            if cover.get('media_url')
        }
    else:
        covers = {}
        cover_urls = {}
        for folder_path, images in images_by_folder.items():
            cover = pick_folder_cover(images)
            if not cover:
                continue
            covers[folder_path] = cover
            cover_urls[folder_path] = cover.get('media_url')

    for item in listed_files:
        if item['media_type'] == 'image':
            item['cover_url'] = item.get('media_url')
            item['cover'] = cover_payload(item)[1]
            continue
        cover_url, cover_data = cover_payload(covers.get(item['folder_path']))
        item['cover_url'] = cover_url
        item['cover'] = cover_data

    current_files = [item for item in listed_files if item['folder_path'] == current_prefix]
    if search and search.strip():
        current_files = listed_files
    current_playable = [item for item in current_files if item['media_type'] in {'audio', 'video'}]
    current_images = [item for item in all_images if item['folder_path'] == current_prefix]
    current_cover_url, current_cover = cover_payload(covers.get(current_prefix))
    current_folder_paths = [
        folder_path for folder_path in folder_paths
        if folder_path.startswith(current_prefix)
        and folder_path != current_prefix
        and folder_path[len(current_prefix):].strip('/').count('/') == 0
    ]

    folder_counts = {}
    for folder_path in folder_paths:
        direct_subfolders = [
            other for other in folder_paths
            if other != folder_path
            and other.startswith(folder_path)
            and other[len(folder_path):].strip('/').count('/') == 0
        ]
        files_in_folder = sum(
            1 for item in playable
            if item['folder_path'] == folder_path
            or item['folder_path'].startswith(folder_path)
        )
        folder_counts[folder_path] = {
            'subfolders': len(direct_subfolders),
            'files': files_in_folder,
        }

    current_folders = [
        {
            'name': folder_name_from_prefix(folder_path),
            'path': folder_path,
            'cover_url': cover_urls.get(folder_path),
            'cover': cover_payload(covers.get(folder_path))[1],
            'subfolders_count': folder_counts.get(folder_path, {}).get('subfolders', 0),
            'files_count': folder_counts.get(folder_path, {}).get('files', 0),
        }
        for folder_path in current_folder_paths
    ]

    return {
        'mode': 'file_manager',
        'cached': True,
        'needs_sync': not (catalog and catalog.last_synced_at),
        'is_syncing': bool(catalog and catalog.is_syncing),
        'last_synced_at': (
            catalog.last_synced_at.isoformat()
            if catalog and catalog.last_synced_at
            else None
        ),
        'last_error': (catalog.last_error if catalog else '') or '',
        'bucket_id': bucket_config.id,
        'bucket_name': bucket_config.bucket_name,
        'root_path': root_prefix,
        'current_path': current_prefix,
        'parent_path': get_parent_path(current_prefix, root_prefix),
        'cover_url': current_cover_url,
        'cover': current_cover,
        'search': search or '',
        'breadcrumbs': build_breadcrumbs(current_prefix, root_prefix),
        'tree': build_folder_tree(root_prefix, folder_paths, cover_urls, folder_counts),
        'folders': current_folders,
        'files': current_files,
        'images': current_images,
        'files_list': listed_files,
        'images_list': all_images,
        'musicas': current_playable,
        'musicas_list': playable,
        'totals': {
            'folders': len(folder_paths),
            'files': len(playable),
            'images': len(all_images),
            'current_folders': len(current_folders),
            'current_files': len([
                item for item in playable if item['folder_path'] == current_prefix
            ]),
            'current_images': len(current_images),
            'audio': sum(1 for item in playable if item['media_type'] == 'audio'),
            'video': sum(1 for item in playable if item['media_type'] == 'video'),
        },
    }


def browse_music_library(bucket_config, prefix=None, search=None):
    catalog = get_catalog(bucket_config)
    root_prefix = effective_root_prefix(bucket_config, probe_r2=False)
    current_prefix = resolve_browse_prefix(
        prefix,
        root_prefix,
        bucket_name=bucket_config.bucket_name,
    )

    if not catalog or not catalog.last_synced_at:
        return assemble_browse(
            bucket_config,
            root_prefix,
            current_prefix,
            folder_paths=[root_prefix] if root_prefix else [],
            all_items=[],
            catalog=catalog,
            search=search,
        )

    folder_paths = list(
        BibliotecaItem.objects.filter(
            bucket=bucket_config,
            kind=BibliotecaItem.KIND_FOLDER,
        ).values_list('key', flat=True),
    )
    file_rows = BibliotecaItem.objects.filter(
        bucket=bucket_config,
        kind=BibliotecaItem.KIND_FILE,
    )
    all_items = [item_from_model(row) for row in file_rows]
    folder_covers_db = load_folder_covers_from_db(bucket_config)
    return assemble_browse(
        bucket_config,
        root_prefix,
        current_prefix,
        folder_paths=folder_paths,
        all_items=all_items,
        catalog=catalog,
        search=search,
        folder_covers_db=folder_covers_db,
    )


def collect_library_from_r2(bucket_config):
    service = S3BucketService(bucket_config)
    root_prefix = resolve_music_root_prefix(bucket_config, service=service)
    all_objects = service.list_all_objects(prefix=root_prefix)
    all_keys = [item['key'] for item in all_objects]
    level = service.list_directory(root_prefix)

    folder_paths = set(extract_folder_paths(all_keys, root_prefix))
    folder_paths.add(root_prefix)
    for folder_path in level['folders']:
        folder_paths.add(normalize_prefix(folder_path))
    for item in level['objects']:
        key = item['key']
        if key.endswith('/') and key.startswith(root_prefix):
            folder_paths.add(normalize_prefix(key))

    all_items = [
        build_media_item(item)
        for item in all_objects
        if is_library_key(item['key']) and not item['key'].endswith('/')
    ]
    return {
        'root_prefix': root_prefix,
        'folder_paths': sorted(folder_paths, key=str.lower),
        'items': all_items,
    }


def replace_catalog(bucket_config, snapshot):
    root_prefix = snapshot['root_prefix']
    folder_paths = {normalize_prefix(path) for path in snapshot['folder_paths'] if path}
    folder_paths.add(root_prefix)
    items = snapshot['items']
    sorted_folder_paths = sorted(folder_paths, key=str.lower)
    folder_covers = resolve_all_folder_covers(sorted_folder_paths, items)

    rows = []
    for path in sorted_folder_paths:
        parent = get_parent_path(path, root_prefix)
        name = folder_name_from_prefix(path) or path
        cover = folder_covers.get(path)
        rows.append(BibliotecaItem(
            bucket=bucket_config,
            kind=BibliotecaItem.KIND_FOLDER,
            key=path,
            name=name[:512],
            title=name[:512],
            folder_path=parent or '',
            extension='',
            media_type='folder',
            size=0,
            last_modified='',
            media_url=(cover.get('media_url') or '')[:2048] if cover else '',
            cover_key=(cover.get('key') or '')[:1024] if cover else '',
        ))

    for item in items:
        rows.append(BibliotecaItem(
            bucket=bucket_config,
            kind=BibliotecaItem.KIND_FILE,
            key=item['key'],
            name=item['name'][:512],
            title=(item.get('title') or '')[:512],
            folder_path=item['folder_path'],
            extension=(item.get('extension') or '')[:16],
            media_type=(item.get('media_type') or 'other')[:16],
            size=item.get('size') or 0,
            last_modified=str(item.get('last_modified') or '')[:64],
            media_url=(item.get('media_url') or '')[:2048],
        ))

    with transaction.atomic():
        BibliotecaItem.objects.filter(bucket=bucket_config).delete()
        BibliotecaItem.objects.bulk_create(rows, batch_size=500)

        catalogo, _created = BibliotecaCatalogo.objects.get_or_create(bucket=bucket_config)
        catalogo.root_path = root_prefix
        catalogo.last_synced_at = timezone.now()
        catalogo.last_error = ''
        catalogo.folders_count = len(folder_paths)
        catalogo.files_count = sum(1 for item in items if item['media_type'] in {'audio', 'video'})
        catalogo.images_count = sum(1 for item in items if item['media_type'] == 'image')
        catalogo.save()
        return catalogo


def refresh_catalog_counts(bucket_config):
    catalogo = get_catalog(bucket_config)
    if catalogo is None:
        return
    items = BibliotecaItem.objects.filter(bucket=bucket_config)
    catalogo.folders_count = items.filter(kind=BibliotecaItem.KIND_FOLDER).count()
    catalogo.files_count = items.filter(
        kind=BibliotecaItem.KIND_FILE,
        media_type__in=['audio', 'video'],
    ).count()
    catalogo.images_count = items.filter(
        kind=BibliotecaItem.KIND_FILE,
        media_type='image',
    ).count()
    catalogo.save(update_fields=['folders_count', 'files_count', 'images_count', 'updated_at'])


def cache_upsert_file(bucket_config, item):
    if not catalog_is_ready(bucket_config):
        return
    BibliotecaItem.objects.update_or_create(
        bucket=bucket_config,
        key=item['key'],
        defaults={
            'kind': BibliotecaItem.KIND_FILE,
            'name': item['name'][:512],
            'title': (item.get('title') or item['name'])[:512],
            'folder_path': item['folder_path'],
            'extension': (item.get('extension') or '')[:16],
            'media_type': (item.get('media_type') or get_media_type(
                os.path.splitext(item['name'])[1].lower(),
            ))[:16],
            'size': item.get('size') or 0,
            'last_modified': str(item.get('last_modified') or '')[:64],
            'media_url': (item.get('media_url') or '')[:2048],
        },
    )
    refresh_catalog_counts(bucket_config)
    rebuild_folder_covers(bucket_config)


def cache_upsert_folder(bucket_config, folder_key, root_prefix):
    if not catalog_is_ready(bucket_config):
        return
    folder_key = normalize_prefix(folder_key)
    parent = get_parent_path(folder_key, root_prefix)
    name = folder_name_from_prefix(folder_key) or folder_key
    BibliotecaItem.objects.update_or_create(
        bucket=bucket_config,
        key=folder_key,
        defaults={
            'kind': BibliotecaItem.KIND_FOLDER,
            'name': name[:512],
            'title': name[:512],
            'folder_path': parent or '',
            'extension': '',
            'media_type': 'folder',
            'size': 0,
            'last_modified': '',
            'media_url': '',
        },
    )
    refresh_catalog_counts(bucket_config)
    rebuild_folder_covers(bucket_config)


def cache_delete_keys(bucket_config, keys):
    if not catalog_is_ready(bucket_config) or not keys:
        return
    BibliotecaItem.objects.filter(bucket=bucket_config, key__in=keys).delete()
    refresh_catalog_counts(bucket_config)
    rebuild_folder_covers(bucket_config)


def sync_music_library(bucket_config):
    catalogo, _created = BibliotecaCatalogo.objects.get_or_create(bucket=bucket_config)
    if catalogo.is_syncing:
        raise BucketServiceError(
            'Sincronização já em andamento.',
            'SYNC_IN_PROGRESS',
        )

    catalogo.is_syncing = True
    catalogo.last_error = ''
    catalogo.save(update_fields=['is_syncing', 'last_error', 'updated_at'])

    try:
        snapshot = collect_library_from_r2(bucket_config)
        catalogo = replace_catalog(bucket_config, snapshot)
        return {
            'synced': True,
            'root_path': catalogo.root_path,
            'last_synced_at': catalogo.last_synced_at.isoformat() if catalogo.last_synced_at else None,
            'folders': catalogo.folders_count,
            'files': catalogo.files_count,
            'images': catalogo.images_count,
        }
    except Exception as exc:
        message = exc.message if isinstance(exc, BucketServiceError) else str(exc)
        BibliotecaCatalogo.objects.filter(pk=catalogo.pk).update(last_error=message)
        if isinstance(exc, BucketServiceError):
            raise
        raise BucketServiceError(message, 'SYNC_ERROR') from exc
    finally:
        BibliotecaCatalogo.objects.filter(pk=catalogo.pk).update(is_syncing=False)


def upload_file_to_folder(bucket_config, prefix, uploaded_file):
    root_prefix = effective_root_prefix(bucket_config, probe_r2=True)
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

    media_url = bucket_config.get_public_url(key)
    extension = os.path.splitext(safe_name)[1].lower()
    cache_upsert_file(bucket_config, {
        'key': key,
        'name': safe_name,
        'title': os.path.splitext(safe_name)[0],
        'folder_path': current_prefix,
        'extension': extension,
        'media_type': get_media_type(extension),
        'size': getattr(uploaded_file, 'size', 0) or 0,
        'last_modified': timezone.now().isoformat(),
        'media_url': media_url or '',
    })

    return {
        'key': key,
        'name': safe_name,
        'folder_path': current_prefix,
        'media_url': media_url,
    }


def move_file(bucket_config, source_key, destination_key):
    root_prefix = effective_root_prefix(bucket_config, probe_r2=True)
    validate_key_in_root(source_key, root_prefix)
    validate_key_in_root(destination_key, root_prefix)

    service = S3BucketService(bucket_config)
    result = service.move_object(source_key, destination_key)

    if catalog_is_ready(bucket_config):
        source = BibliotecaItem.objects.filter(bucket=bucket_config, key=source_key).first()
        cache_delete_keys(bucket_config, [source_key])
        dest_name = os.path.basename(destination_key.rstrip('/'))
        dest_folder = normalize_prefix('/'.join(destination_key.split('/')[:-1]))
        extension = os.path.splitext(dest_name)[1].lower()
        cache_upsert_file(bucket_config, {
            'key': destination_key,
            'name': dest_name,
            'title': os.path.splitext(dest_name)[0],
            'folder_path': dest_folder,
            'extension': extension,
            'media_type': source.media_type if source else get_media_type(extension),
            'size': source.size if source else 0,
            'last_modified': timezone.now().isoformat(),
            'media_url': bucket_config.get_public_url(destination_key) or '',
        })
    return result


def delete_files(bucket_config, keys):
    root_prefix = effective_root_prefix(bucket_config, probe_r2=True)
    for key in keys:
        validate_key_in_root(key, root_prefix)

    service = S3BucketService(bucket_config)
    result = service.delete_objects(keys)
    cache_delete_keys(bucket_config, keys)
    return result


def create_folder(bucket_config, prefix, folder_name):
    root_prefix = effective_root_prefix(bucket_config, probe_r2=True)
    current_prefix = resolve_browse_prefix(
        prefix,
        root_prefix,
        bucket_name=bucket_config.bucket_name,
    )
    safe_name = re.sub(r'[^\w.\-]', '_', folder_name.strip())
    folder_key = f'{current_prefix}{safe_name}/'
    validate_key_in_root(folder_key, root_prefix)

    service = S3BucketService(bucket_config)
    result = service.create_folder(folder_key)
    cache_upsert_folder(bucket_config, folder_key, root_prefix)
    return result
