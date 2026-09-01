from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from buckets.views import (
    BucketConfigViewSet,
    BucketObjectDeleteView,
    BucketObjectListView,
    BucketObjectMoveView,
    BucketObjectUploadView,
    BucketTestConnectionView,
)

router = DefaultRouter()
router.register('buckets', BucketConfigViewSet, basename='bucket')

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='api-token-auth'),
    path('', include(router.urls)),
    path(
        'buckets/<int:pk>/test-connection/',
        BucketTestConnectionView.as_view(),
        name='bucket-test-connection',
    ),
    path(
        'buckets/<int:pk>/objects/',
        BucketObjectListView.as_view(),
        name='bucket-object-list',
    ),
    path(
        'buckets/<int:pk>/objects/upload/',
        BucketObjectUploadView.as_view(),
        name='bucket-object-upload',
    ),
    path(
        'buckets/<int:pk>/objects/move/',
        BucketObjectMoveView.as_view(),
        name='bucket-object-move',
    ),
    path(
        'buckets/<int:pk>/objects/delete/',
        BucketObjectDeleteView.as_view(),
        name='bucket-object-delete',
    ),
]
