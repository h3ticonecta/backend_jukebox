from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from maquinas.models import Maquina
from maquinas.serializers import (
    MaquinaAuthSerializer,
    MaquinaSerializer,
    MaquinaWriteSerializer,
)


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
