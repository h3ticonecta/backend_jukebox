from rest_framework import serializers

from pagamentos.models import MercadoPagoConfig, PixCobranca


class PixCobrancaCreateSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    descricao = serializers.CharField(required=False, allow_blank=True, max_length=255)
    maquina_id = serializers.IntegerField(required=False)


class MercadoPagoConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MercadoPagoConfig
        fields = [
            'id',
            'nome',
            'public_key',
            'id_conta',
            'usar_sandbox',
            'is_active',
            'webhook_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MercadoPagoConfigWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MercadoPagoConfig
        fields = [
            'nome',
            'access_token',
            'public_key',
            'id_conta',
            'usar_sandbox',
            'is_active',
            'webhook_url',
        ]

    def validate(self, attrs):
        token = attrs.get('access_token')
        if token is not None and not str(token).strip():
            raise serializers.ValidationError({'access_token': 'Informe o access token.'})
        return attrs

    def update(self, instance, validated_data):
        token = validated_data.get('access_token')
        if token is not None and not str(token).strip():
            validated_data.pop('access_token')
        return super().update(instance, validated_data)


class PixCobrancaListSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source='maquina.nome_jukebox', read_only=True)

    class Meta:
        model = PixCobranca
        fields = [
            'id',
            'maquina',
            'maquina_nome',
            'valor',
            'status',
            'mp_payment_id',
            'credito_id',
            'created_at',
            'approved_at',
        ]
        read_only_fields = fields
