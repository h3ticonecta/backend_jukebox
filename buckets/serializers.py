from rest_framework import serializers

from buckets.models import BucketConfig, BucketProvider


class BucketConfigSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)

    class Meta:
        model = BucketConfig
        fields = [
            'id',
            'name',
            'provider',
            'provider_display',
            'endpoint_url',
            'bucket_name',
            'access_key_id',
            'region_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BucketConfigWriteSerializer(serializers.ModelSerializer):
    secret_access_key = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = BucketConfig
        fields = [
            'name',
            'provider',
            'endpoint_url',
            'bucket_name',
            'access_key_id',
            'secret_access_key',
            'region_name',
            'is_active',
        ]

    def validate_provider(self, value):
        if value not in BucketProvider.values:
            raise serializers.ValidationError('Provedor inválido.')
        return value

    def create(self, validated_data):
        secret = validated_data.pop('secret_access_key', None)
        if not secret:
            raise serializers.ValidationError(
                {'secret_access_key': 'Campo obrigatório na criação.'},
            )
        return BucketConfig.objects.create(secret_access_key=secret, **validated_data)

    def update(self, instance, validated_data):
        secret = validated_data.pop('secret_access_key', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if secret:
            instance.secret_access_key = secret
        instance.save()
        return instance


class BucketObjectMoveSerializer(serializers.Serializer):
    source_key = serializers.CharField(max_length=1024)
    destination_key = serializers.CharField(max_length=1024)


class BucketObjectDeleteSerializer(serializers.Serializer):
    keys = serializers.ListField(
        child=serializers.CharField(max_length=1024),
        allow_empty=False,
    )


class BucketObjectUploadSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=1024, required=False, allow_blank=True)
    file = serializers.FileField()
