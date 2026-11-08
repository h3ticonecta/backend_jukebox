from rest_framework import serializers

from maquinas.models import RoletaPremioFaixa


class RoletaPremioSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=RoletaPremioFaixa.TipoPremio.choices)
    quantidade = serializers.IntegerField(min_value=1)
    peso = serializers.IntegerField(min_value=1)
    ordem = serializers.IntegerField(required=False, min_value=0)


class RoletaFaixaSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    giros_liberados = serializers.IntegerField(min_value=0)
    ordem = serializers.IntegerField(required=False, min_value=0)
    premios = RoletaPremioSerializer(many=True, allow_empty=True)


class RoletaProbabilidadesSerializer(serializers.Serializer):
    premio_mais_2_musicas = serializers.IntegerField(min_value=0, required=False)
    premio_mais_1_musica = serializers.IntegerField(min_value=0, required=False)
    bonus_recarga_50pct = serializers.IntegerField(min_value=0, required=False)
    tente_novamente = serializers.IntegerField(min_value=0, required=False)
    nao_foi_dessa_vez = serializers.IntegerField(min_value=0, required=False)


class RoletaRegrasSerializer(serializers.Serializer):
    creditos_minimos_girar = serializers.IntegerField(min_value=0, required=False)
    max_premio_mais_2_musicas_dia_percent = serializers.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
    )


class RoletaConfigWriteSerializer(serializers.Serializer):
    ativada = serializers.BooleanField(required=False)
    probabilidades = RoletaProbabilidadesSerializer(required=False)
    regras = RoletaRegrasSerializer(required=False)
    faixas_valor = RoletaFaixaSerializer(many=True, required=False)
