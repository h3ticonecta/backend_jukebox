from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from buckets.exceptions import BucketServiceError
from buckets.models import BucketConfig
from buckets.serializers import (
    BucketConfigSerializer,
    BucketConfigWriteSerializer,
    BucketObjectDeleteSerializer,
    BucketObjectMoveSerializer,
    BucketObjectUploadSerializer,
)
from buckets.services import S3BucketService


def get_bucket_service(bucket_id):
    bucket_config = get_object_or_404(BucketConfig, pk=bucket_id, is_active=True)
    return S3BucketService(bucket_config), bucket_config


def bucket_error_response(exc):
    return Response(
        {
            'error': {
                'code': exc.code,
                'message': exc.message,
            },
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


class BucketConfigViewSet(viewsets.ModelViewSet):
    queryset = BucketConfig.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BucketConfigWriteSerializer
        return BucketConfigSerializer


class BucketTestConnectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            service, bucket_config = get_bucket_service(pk)
            result = service.test_connection()
            return Response({
                'bucket_id': bucket_config.id,
                'bucket_name': bucket_config.bucket_name,
                **result,
            })
        except BucketServiceError as exc:
            return bucket_error_response(exc)


class BucketObjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        prefix = request.query_params.get('prefix', '')
        continuation_token = request.query_params.get('continuation_token')
        max_keys = min(int(request.query_params.get('max_keys', 100)), 1000)

        try:
            service, bucket_config = get_bucket_service(pk)
            result = service.list_objects(
                prefix=prefix,
                continuation_token=continuation_token,
                max_keys=max_keys,
            )
            return Response({
                'bucket_id': bucket_config.id,
                'bucket_name': bucket_config.bucket_name,
                **result,
            })
        except BucketServiceError as exc:
            return bucket_error_response(exc)


class BucketObjectUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        serializer = BucketObjectUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        key = serializer.validated_data.get('key') or uploaded_file.name

        try:
            service, bucket_config = get_bucket_service(pk)
            result = service.upload_object(
                key=key,
                file_obj=uploaded_file.file,
                content_type=uploaded_file.content_type,
            )
            return Response(
                {
                    'bucket_id': bucket_config.id,
                    **result,
                },
                status=status.HTTP_201_CREATED,
            )
        except BucketServiceError as exc:
            return bucket_error_response(exc)


class BucketObjectMoveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = BucketObjectMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service, bucket_config = get_bucket_service(pk)
            result = service.move_object(
                source_key=serializer.validated_data['source_key'],
                destination_key=serializer.validated_data['destination_key'],
            )
            return Response({
                'bucket_id': bucket_config.id,
                **result,
            })
        except BucketServiceError as exc:
            return bucket_error_response(exc)


class BucketObjectDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = BucketObjectDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service, bucket_config = get_bucket_service(pk)
            result = service.delete_objects(keys=serializer.validated_data['keys'])
            return Response({
                'bucket_id': bucket_config.id,
                **result,
            })
        except BucketServiceError as exc:
            return bucket_error_response(exc)
