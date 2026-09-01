from rest_framework import serializers

from buckets.models import BucketConfig
from musicas.models import Musica


class MusicaSerializer(serializers.ModelSerializer):
    audio_url = serializers.ReadOnlyField()
    bucket_id = serializers.IntegerField(source='bucket.id', read_only=True)
    bucket_name = serializers.CharField(source='bucket.name', read_only=True)

    class Meta:
        model = Musica
        fields = [
            'id',
            'title',
            'artist',
            'album',
            'storage_key',
            'audio_url',
            'duration_seconds',
            'file_size',
            'content_type',
            'bucket_id',
            'bucket_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'storage_key',
            'audio_url',
            'file_size',
            'content_type',
            'created_at',
            'updated_at',
        ]


class MusicaWriteSerializer(serializers.ModelSerializer):
    bucket_id = serializers.PrimaryKeyRelatedField(
        queryset=BucketConfig.objects.filter(is_active=True),
        source='bucket',
    )

    class Meta:
        model = Musica
        fields = [
            'title',
            'artist',
            'album',
            'bucket_id',
            'duration_seconds',
            'is_active',
        ]

    def validate_bucket_id(self, value):
        if not value.public_base_url:
            raise serializers.ValidationError(
                'O bucket selecionado não possui URL pública configurada.',
            )
        return value


class MusicaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        try:
            Musica.validate_audio_extension(value.name)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value
