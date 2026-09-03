from rest_framework import serializers

from maquinas.models import Credito, CreditoOrigem, Maquina, MusicaTocada
from maquinas.teclas import ACOES_VALIDAS, normalizar_teclas


class TeclaSerializer(serializers.Serializer):
    acao = serializers.CharField()
    label = serializers.CharField()
    tecla = serializers.CharField(max_length=32)


class MaquinaSerializer(serializers.ModelSerializer):
    teclas = serializers.SerializerMethodField()

    class Meta:
        model = Maquina
        fields = [
            'id',
            'nome_jukebox',
            'usuario',
            'is_active',
            'teclas',
            'last_login_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'last_login_at', 'created_at', 'updated_at', 'teclas']

    def get_teclas(self, obj):
        return obj.get_teclas()


class MaquinaWriteSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=4)
    teclas = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text='Lista de atalhos: [{ "acao": "cima", "tecla": "Q" }, ...]',
    )

    class Meta:
        model = Maquina
        fields = [
            'nome_jukebox',
            'usuario',
            'senha',
            'is_active',
            'teclas',
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

    def validate_teclas(self, value):
        if value is None:
            return value
        acoes = []
        for item in value:
            acao = (item.get('acao') or '').strip()
            if not acao:
                raise serializers.ValidationError('Cada atalho precisa de "acao".')
            if acao not in ACOES_VALIDAS:
                raise serializers.ValidationError(f'Ação inválida: {acao}')
            tecla = str(item.get('tecla', '')).strip()
            if not tecla:
                raise serializers.ValidationError(f'Tecla obrigatória para "{acao}".')
            acoes.append({'acao': acao, 'tecla': tecla})
        return normalizar_teclas(acoes)

    def create(self, validated_data):
        senha = validated_data.pop('senha', None)
        teclas = validated_data.pop('teclas', None)
        if not senha:
            raise serializers.ValidationError({'senha': 'Campo obrigatório na criação.'})
        maquina = Maquina(**validated_data)
        if teclas is not None:
            maquina.teclas = teclas
        maquina.set_password(senha)
        maquina.rotate_token()
        maquina.save()
        return maquina

    def update(self, instance, validated_data):
        senha = validated_data.pop('senha', None)
        teclas = validated_data.pop('teclas', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if teclas is not None:
            instance.teclas = teclas
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
