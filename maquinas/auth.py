from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from maquinas.models import Maquina


class MaquinaAuthUser:
    """Usuário proxy para jukebox autenticada via token da máquina."""

    def __init__(self, maquina):
        self.maquina = maquina

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    is_staff = False
    is_superuser = False


class MaquinaAuthentication(BaseAuthentication):
    """Aceita `Authorization: Maquina <api_token>` da jukebox."""

    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        if not header or ' ' not in header:
            return None

        scheme, token = header.split(' ', 1)
        token = token.strip()
        if not token or scheme.lower() not in ('maquina', 'machine'):
            return None

        maquina = Maquina.objects.filter(api_token=token, is_active=True).first()
        if maquina is None:
            raise AuthenticationFailed('Token de máquina inválido.')

        return MaquinaAuthUser(maquina), token


def get_maquina_from_request(request):
    header = request.META.get('HTTP_AUTHORIZATION', '')
    if not header or ' ' not in header:
        return None

    scheme, token = header.split(' ', 1)
    token = token.strip()
    if not token:
        return None

    if scheme.lower() in ('maquina', 'machine'):
        maquina = Maquina.objects.filter(api_token=token, is_active=True).first()
        if maquina is None:
            raise AuthenticationFailed('Token de máquina inválido.')
        return maquina

    if scheme.lower() == 'token' and not Token.objects.filter(key=token).exists():
        maquina = Maquina.objects.filter(api_token=token, is_active=True).first()
        if maquina is not None:
            return maquina

    return None


def resolve_maquina(request, require=True):
    maquina = get_maquina_from_request(request)
    if maquina is not None:
        return maquina

    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        maquina_id = request.data.get('maquina_id') or request.query_params.get('maquina_id')
        if maquina_id:
            maquina = Maquina.objects.filter(pk=maquina_id, is_active=True).first()
            if maquina is None:
                raise AuthenticationFailed('Máquina não encontrada ou inativa.')
            return maquina
        if require:
            raise AuthenticationFailed('Informe maquina_id ou use o token da máquina.')
        return None

    if require:
        raise AuthenticationFailed('Autenticação da máquina obrigatória.')
    return None
