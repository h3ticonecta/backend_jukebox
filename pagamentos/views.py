from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from maquinas.auth import resolve_maquina
from pagamentos.exceptions import PagamentoServiceError
from pagamentos.models import MercadoPagoConfig, PixCobranca
from pagamentos.serializers import (
    MercadoPagoConfigSerializer,
    MercadoPagoConfigWriteSerializer,
    PixCobrancaCreateSerializer,
    PixCobrancaListSerializer,
)
from pagamentos.services import (
    criar_cobranca_pix,
    pix_cobranca_payload,
    processar_webhook_mp,
    sincronizar_cobranca,
)


def payment_error_response(exc, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {'error': {'code': exc.code, 'message': exc.message}},
        status=status_code,
    )


class MercadoPagoConfigViewSet(viewsets.ModelViewSet):
    queryset = MercadoPagoConfig.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return MercadoPagoConfigWriteSerializer
        return MercadoPagoConfigSerializer


class PixCobrancaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PixCobranca.objects.select_related('maquina').all()
    serializer_class = PixCobrancaListSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='qrcode', permission_classes=[AllowAny])
    def qrcode(self, request):
        """POST /api/v1/pagamentos/pix/qrcode/ — gera QR PIX (jukebox ou admin com maquina_id)."""
        serializer = PixCobrancaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            maquina = resolve_maquina(request)
        except AuthenticationFailed as exc:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            cobranca = criar_cobranca_pix(
                maquina,
                serializer.validated_data['valor'],
                descricao=serializer.validated_data.get('descricao') or '',
            )
        except PagamentoServiceError as exc:
            code = status.HTTP_503_SERVICE_UNAVAILABLE if exc.code == 'MP_NOT_CONFIGURED' else status.HTTP_400_BAD_REQUEST
            return payment_error_response(exc, status_code=code)

        return Response(pix_cobranca_payload(cobranca), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='sincronizar', permission_classes=[AllowAny])
    def sincronizar(self, request, pk=None):
        """Consulta status no Mercado Pago e atualiza a cobrança."""
        cobranca = self.get_object()
        try:
            maquina = resolve_maquina(request, require=False)
        except AuthenticationFailed as exc:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if maquina is not None and cobranca.maquina_id != maquina.id:
            return Response(
                {'error': {'code': 'FORBIDDEN', 'message': 'Cobrança de outra máquina.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        if maquina is None and not request.user.is_authenticated:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': 'Autenticação obrigatória.'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            cobranca = sincronizar_cobranca(cobranca)
        except PagamentoServiceError as exc:
            return payment_error_response(exc)

        return Response(pix_cobranca_payload(cobranca))

    def retrieve(self, request, *args, **kwargs):
        cobranca = self.get_object()
        try:
            maquina = resolve_maquina(request, require=False)
        except AuthenticationFailed as exc:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if maquina is not None and cobranca.maquina_id != maquina.id:
            return Response(
                {'error': {'code': 'FORBIDDEN', 'message': 'Cobrança de outra máquina.'}},
                status=status.HTTP_403_FORBIDDEN,
            )
        if maquina is None and not request.user.is_authenticated:
            return Response(
                {'error': {'code': 'UNAUTHORIZED', 'message': 'Autenticação obrigatória.'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(pix_cobranca_payload(cobranca))


def extrair_webhook_mercadopago(request):
    query = request.query_params
    topic = query.get('topic') or query.get('type')
    payment_id = query.get('id') or query.get('data.id')

    body = request.data if isinstance(request.data, dict) else {}
    if not payment_id:
        data = body.get('data') if isinstance(body.get('data'), dict) else {}
        payment_id = data.get('id')
    if not topic:
        topic = body.get('type') or body.get('action')

    try:
        payment_id = int(payment_id) if payment_id is not None and payment_id != '' else None
    except (TypeError, ValueError):
        payment_id = None

    return payment_id, topic


@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhookView(APIView):
    """Mercado Pago exige HTTP 2xx; testes usam ID fictício (ex.: 123456)."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payment_id, topic = extrair_webhook_mercadopago(request)

        try:
            result = processar_webhook_mp(payment_id=payment_id, topic=topic)
        except PagamentoServiceError as exc:
            return Response(
                {
                    'received': True,
                    'ignored': True,
                    'error': {'code': exc.code, 'message': exc.message},
                },
                status=status.HTTP_200_OK,
            )

        payload = {'received': True}
        if result and result.get('ignored'):
            payload['ignored'] = True
            payload['detail'] = result
        elif result:
            payload['cobranca'] = result
        return Response(payload, status=status.HTTP_200_OK)

    def get(self, request):
        """Mercado Pago também pode chamar via GET em alguns fluxos."""
        return self.post(request)
