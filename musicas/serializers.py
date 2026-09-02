from rest_framework import serializers

from musicas.models import Musica


class FileManagerUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    prefix = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_file(self, value):
        try:
            Musica.validate_audio_extension(value.name)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value


class FileManagerMoveSerializer(serializers.Serializer):
    source_key = serializers.CharField(max_length=1024)
    destination_key = serializers.CharField(max_length=1024)


class FileManagerDeleteSerializer(serializers.Serializer):
    keys = serializers.ListField(
        child=serializers.CharField(max_length=1024),
        allow_empty=False,
    )


class FileManagerCreateFolderSerializer(serializers.Serializer):
    prefix = serializers.CharField(required=False, allow_blank=True, default='')
    name = serializers.CharField(max_length=255)
