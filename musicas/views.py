from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from maquinas.auth import MaquinaAuthentication

from buckets.exceptions import BucketServiceError
from musicas.serializers import (
    FileManagerCreateFolderSerializer,
    FileManagerDeleteSerializer,
    FileManagerMoveSerializer,
    FileManagerUploadSerializer,
)
from musicas.services import (
    browse_music_library,
    create_folder,
    delete_files,
    get_music_bucket,
    move_file,
    sync_music_library,
    upload_file_to_folder,
)


def error_response(exc, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {'error': {'code': exc.code, 'message': exc.message}},
        status=status_code,
    )


class MusicaFileManagerViewSet(viewsets.ViewSet):
    """File manager de músicas no R2 — navegação, upload, mover e excluir."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_authenticators(self):
        if getattr(self, 'action', None) in ('list', 'browse'):
            auth_classes = [TokenAuthentication, MaquinaAuthentication, SessionAuthentication]
        else:
            auth_classes = [SessionAuthentication, TokenAuthentication]
        return [auth() for auth in auth_classes]

    def list(self, request):
        """GET /api/v1/musicas/ — navega o catálogo em cache no PostgreSQL."""
        return self._browse(request)

    @action(detail=False, methods=['get'], url_path='browse')
    def browse(self, request):
        """Alias de list para compatibilidade."""
        return self._browse(request)

    def _browse(self, request):
        bucket_id = request.query_params.get('bucket_id')
        prefix = request.query_params.get('prefix', '')
        search = request.query_params.get('q', '').strip()

        try:
            bucket = get_music_bucket(int(bucket_id) if bucket_id else None)
            return Response(browse_music_library(bucket, prefix=prefix, search=search))
        except BucketServiceError as exc:
            return error_response(exc)

    @action(detail=False, methods=['post'], url_path='sync')
    def sync(self, request):
        """POST /api/v1/musicas/sync/ — relê o R2 e atualiza o catálogo no PostgreSQL."""
        bucket_id = request.data.get('bucket_id') or request.query_params.get('bucket_id')

        try:
            bucket = get_music_bucket(int(bucket_id) if bucket_id else None)
            result = sync_music_library(bucket)
            return Response({'bucket_id': bucket.id, **result})
        except BucketServiceError as exc:
            status_code = (
                status.HTTP_409_CONFLICT
                if exc.code == 'SYNC_IN_PROGRESS'
                else status.HTTP_400_BAD_REQUEST
            )
            return error_response(exc, status_code=status_code)

    @action(
        detail=False,
        methods=['post'],
        url_path='upload',
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload(self, request):
        """POST /api/v1/musicas/upload/ — envia arquivo para a pasta atual."""
        serializer = FileManagerUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bucket_id = request.data.get('bucket_id') or request.query_params.get('bucket_id')

        try:
            bucket = get_music_bucket(int(bucket_id) if bucket_id else None)
            result = upload_file_to_folder(
                bucket,
                prefix=serializer.validated_data.get('prefix', ''),
                uploaded_file=serializer.validated_data['file'],
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except BucketServiceError as exc:
            return error_response(exc)
        except ValueError as exc:
            return error_response(
                BucketServiceError(str(exc), 'VALIDATION_ERROR'),
            )

    @action(detail=False, methods=['post'], url_path='move')
    def move(self, request):
        """POST /api/v1/musicas/move/ — move arquivo no R2."""
        serializer = FileManagerMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bucket_id = request.data.get('bucket_id')

        try:
            bucket = get_music_bucket(int(bucket_id) if bucket_id else None)
            result = move_file(
                bucket,
                source_key=serializer.validated_data['source_key'],
                destination_key=serializer.validated_data['destination_key'],
            )
            return Response({'bucket_id': bucket.id, **result})
        except BucketServiceError as exc:
            return error_response(exc)

    @action(detail=False, methods=['post'], url_path='delete')
    def delete(self, request):
        """POST /api/v1/musicas/delete/ — exclui arquivos do R2."""
        serializer = FileManagerDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bucket_id = request.data.get('bucket_id')

        try:
            bucket = get_music_bucket(int(bucket_id) if bucket_id else None)
            result = delete_files(bucket, keys=serializer.validated_data['keys'])
            return Response({'bucket_id': bucket.id, **result})
        except BucketServiceError as exc:
            return error_response(exc)

    @action(detail=False, methods=['post'], url_path='folders')
    def folders(self, request):
        """POST /api/v1/musicas/folders/ — cria subpasta no R2."""
        serializer = FileManagerCreateFolderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bucket_id = request.data.get('bucket_id')

        try:
            bucket = get_music_bucket(int(bucket_id) if bucket_id else None)
            result = create_folder(
                bucket,
                prefix=serializer.validated_data.get('prefix', ''),
                folder_name=serializer.validated_data['name'],
            )
            return Response(
                {'bucket_id': bucket.id, **result},
                status=status.HTTP_201_CREATED,
            )
        except BucketServiceError as exc:
            return error_response(exc)
