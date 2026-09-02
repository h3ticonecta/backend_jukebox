from django.urls import include, path
from rest_framework.routers import DefaultRouter

from maquinas.views import MaquinaViewSet

router = DefaultRouter()
router.register('maquinas', MaquinaViewSet, basename='maquina')

urlpatterns = [
    path('', include(router.urls)),
]
