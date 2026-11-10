from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pagamentos.views import (
    MercadoPagoConfigViewSet,
    MercadoPagoWebhookView,
    PixCobrancaViewSet,
    PixCreditoOpcaoViewSet,
)

router = DefaultRouter()
router.register('pagamentos/mercadopago', MercadoPagoConfigViewSet, basename='mercadopago-config')
router.register('pagamentos/pix-creditos', PixCreditoOpcaoViewSet, basename='pix-creditos')
router.register('pagamentos/pix', PixCobrancaViewSet, basename='pix-cobranca')

urlpatterns = [
    path(
        'pagamentos/webhook/mercadopago/',
        MercadoPagoWebhookView.as_view(),
        name='mercadopago-webhook',
    ),
    path('', include(router.urls)),
]
