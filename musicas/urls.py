from django.urls import include, path
from rest_framework.routers import DefaultRouter

from musicas.views import MusicaUploadView, MusicaViewSet

router = DefaultRouter()
router.register('musicas', MusicaViewSet, basename='musica')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'musicas/<int:pk>/upload/',
        MusicaUploadView.as_view(),
        name='musica-upload',
    ),
]
