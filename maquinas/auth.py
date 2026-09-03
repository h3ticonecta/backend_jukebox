from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from maquinas.models import Maquina


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
