from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from maquinas.auth import resolve_maquina
from maquinas.models import Credito, Maquina, MusicaTocada
from maquinas.serializers import (
    CreditoCreateSerializer,
    CreditoSerializer,
    MaquinaAuthSerializer,
    MaquinaSerializer,
    MaquinaWriteSerializer,
    MusicaTocadaCreateSerializer,
    MusicaTocadaSerializer,
)
from maquinas.services import relatorio_faturamento, relatorio_mais_tocadas


class MaquinaViewSet(viewsets.ModelViewSet):
    queryset = Maquina.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return MaquinaWriteSerializer
        return MaquinaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            MaquinaSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(MaquinaSerializer(serializer.instance).data)

    @action(detail=False, methods=['post'], url_path='auth', permission_classes=[AllowAny])
    def auth(self, request):
        """POST /api/v1/maquinas/auth/ — vincula a jukebox pelo usuário e senha."""
        serializer = MaquinaAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.validated_data['usuario'].strip()
        senha = serializer.validated_data['senha']
        maquina = Maquina.objects.filter(usuario__iexact=usuario).first()

        if maquina is None or not maquina.check_password(senha):
            return Response(
                {'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Usuário ou senha inválidos.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not maquina.is_active:
            return Response(
                {'error': {'code': 'MACHINE_INACTIVE', 'message': 'Esta máquina está inativa.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        maquina.last_login_at = timezone.now()
        maquina.save(update_fields=['last_login_at', 'updated_at'])

        return Response({
            'id': maquina.id,
            'nome_jukebox': maquina.nome_jukebox,
            'usuario': maquina.usuario,
            'token': maquina.api_token,
        })

    @action(detail=False, methods=['post'], url_path='creditos', permission_classes=[AllowAny])
    def creditos(self, request):
        """POST /api/v1/maquinas/creditos/ — registra dinheiro inserido na máquina."""
        serializer = CreditoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            maquina = resolve_maquina(request)
        except AuthenticationFailed as exc:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        credito = Credito.objects.create(
            maquina=maquina,
            valor=serializer.validated_data['valor'],
            origem=serializer.validated_data.get('origem') or 'moeda',
            observacao=serializer.validated_data.get('observacao') or '',
        )
        return Response(CreditoSerializer(credito).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='tocadas', permission_classes=[AllowAny])
    def tocadas(self, request):
        """POST /api/v1/maquinas/tocadas/ — registra a música escolhida para tocar."""
        serializer = MusicaTocadaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            maquina = resolve_maquina(request)
        except AuthenticationFailed as exc:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = serializer.validated_data
        nome = data.get('musica_nome') or data['musica_key'].rstrip('/').split('/')[-1]
        tocada = MusicaTocada.objects.create(
            maquina=maquina,
            musica_key=data['musica_key'],
            musica_nome=nome,
            titulo=data.get('titulo') or nome,
            pasta=data.get('pasta') or '',
            media_type=data.get('media_type') or 'audio',
            media_url=data.get('media_url') or '',
            cover_url=data.get('cover_url') or '',
            valor=data.get('valor'),
        )
        return Response(MusicaTocadaSerializer(tocada).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='relatorio-faturamento')
    def relatorio_faturamento_view(self, request):
        """GET /api/v1/maquinas/relatorio-faturamento/"""
        return Response(relatorio_faturamento(
            maquina_id=request.query_params.get('maquina_id'),
            inicio=request.query_params.get('inicio'),
            fim=request.query_params.get('fim'),
        ))

    @action(detail=False, methods=['get'], url_path='relatorio-mais-tocadas')
    def relatorio_mais_tocadas_view(self, request):
        """GET /api/v1/maquinas/relatorio-mais-tocadas/"""
        return Response(relatorio_mais_tocadas(
            maquina_id=request.query_params.get('maquina_id'),
            inicio=request.query_params.get('inicio'),
            fim=request.query_params.get('fim'),
            limit=request.query_params.get('limit') or 20,
        ))
