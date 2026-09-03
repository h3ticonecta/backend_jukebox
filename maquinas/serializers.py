from rest_framework import serializers

from maquinas.models import Credito, CreditoOrigem, Maquina, MusicaTocada


class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = [
            'id',
            'nome_jukebox',
            'usuario',
            'is_active',
            'last_login_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'last_login_at', 'created_at', 'updated_at']


class MaquinaWriteSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=4)

    class Meta:
        model = Maquina
        fields = [
            'nome_jukebox',
            'usuario',
            'senha',
            'is_active',
        ]

    def validate_usuario(self, value):
        usuario = value.strip()
        if not usuario:
            raise serializers.ValidationError('Informe o usuário da máquina.')
        queryset = Maquina.objects.filter(usuario__iexact=usuario)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Já existe uma máquina com este usuário.')
        return usuario

    def create(self, validated_data):
        senha = validated_data.pop('senha', None)
        if not senha:
            raise serializers.ValidationError({'senha': 'Campo obrigatório na criação.'})
        maquina = Maquina(**validated_data)
        maquina.set_password(senha)
        maquina.rotate_token()
        maquina.save()
        return maquina

    def update(self, instance, validated_data):
        senha = validated_data.pop('senha', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if senha:
            instance.set_password(senha)
            instance.rotate_token()
        instance.save()
        return instance


class MaquinaAuthSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    senha = serializers.CharField()


class CreditoSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source='maquina.nome_jukebox', read_only=True)

    class Meta:
        model = Credito
        fields = [
            'id',
            'maquina',
            'maquina_nome',
            'valor',
            'origem',
            'observacao',
            'created_at',
        ]
        read_only_fields = ['id', 'maquina', 'created_at']


class CreditoCreateSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    origem = serializers.ChoiceField(choices=CreditoOrigem.choices, required=False, default=CreditoOrigem.MOEDA)
    observacao = serializers.CharField(required=False, allow_blank=True, default='', max_length=255)
    maquina_id = serializers.IntegerField(required=False)


class MusicaTocadaSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source='maquina.nome_jukebox', read_only=True)

    class Meta:
        model = MusicaTocada
        fields = [
            'id',
            'maquina',
            'maquina_nome',
            'musica_key',
            'musica_nome',
            'titulo',
            'pasta',
            'media_type',
            'media_url',
            'cover_url',
            'valor',
            'created_at',
        ]
        read_only_fields = ['id', 'maquina', 'created_at']


class MusicaTocadaCreateSerializer(serializers.Serializer):
    musica_key = serializers.CharField(max_length=1024)
    musica_nome = serializers.CharField(max_length=512, required=False, allow_blank=True, default='')
    titulo = serializers.CharField(max_length=512, required=False, allow_blank=True, default='')
    pasta = serializers.CharField(max_length=1024, required=False, allow_blank=True, default='')
    media_type = serializers.CharField(max_length=16, required=False, default='audio')
    media_url = serializers.CharField(max_length=2048, required=False, allow_blank=True, default='')
    cover_url = serializers.CharField(max_length=2048, required=False, allow_blank=True, default='')
    valor = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=0,
    )
    maquina_id = serializers.IntegerField(required=False)

    def validate_musica_key(self, value):
        key = value.strip()
        if not key:
            raise serializers.ValidationError('Informe a música escolhida (musica_key).')
        return key
