from buckets.exceptions import BucketServiceError
from buckets.services import S3BucketService
from musicas.models import Musica


def upload_musica_file(musica, uploaded_file):
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
