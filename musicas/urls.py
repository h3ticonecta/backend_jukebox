from django.urls import include, path
from rest_framework.routers import DefaultRouter

from musicas.views import MusicaFileManagerViewSet

router = DefaultRouter()
router.register('musicas', MusicaFileManagerViewSet, basename='musica')

urlpatterns = [
    path('', include(router.urls)),
]
