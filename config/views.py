from django.db import connection
from django.http import JsonResponse


def index(request):
    return JsonResponse({
        'service': 'backend_jukebox',
        'status': 'running',
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
            'api_v1': '/api/v1/',
            'buckets': '/api/v1/buckets/',
            'musicas': '/api/v1/musicas/',
            'maquinas': '/api/v1/maquinas/',
        },
    })


def health(request):
    return JsonResponse({
        'status': 'ok',
        'database': connection.vendor,
        'persistent': connection.vendor == 'postgresql',
    })