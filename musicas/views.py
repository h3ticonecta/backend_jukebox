from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from buckets.exceptions import BucketServiceError
from musicas.models import Musica
from musicas.serializers import (
    MusicaSerializer,
    MusicaUploadSerializer,
    MusicaWriteSerializer,
)
from musicas.services import delete_musica_file, upload_musica_file


class MusicaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Musica.objects.select_related('bucket').all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return MusicaWriteSerializer
        return MusicaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        artist = self.request.query_params.get('artist')
        album = self.request.query_params.get('album')
        is_active = self.request.query_params.get('is_active')

        if artist:
            queryset = queryset.filter(artist__icontains=artist)
        if album:
            queryset = queryset.filter(album__icontains=album)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ('true', '1', 'yes'))
        return queryset

    def perform_destroy(self, instance):
        try:
            delete_musica_file(instance)
        except BucketServiceError:
            pass
        instance.delete()


class MusicaUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        musica = get_object_or_404(Musica, pk=pk)
        serializer = MusicaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            upload_musica_file(musica, serializer.validated_data['file'])
        except BucketServiceError as exc:
            return Response(
                {'error': {'code': exc.code, 'message': exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
            return Response(
                {'error': {'code': 'VALIDATION_ERROR', 'message': str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(MusicaSerializer(musica).data, status=status.HTTP_200_OK)
