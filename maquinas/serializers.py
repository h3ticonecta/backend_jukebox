from rest_framework import serializers

from maquinas.models import Maquina


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
