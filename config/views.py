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
        },
    })


def health(request):
    return JsonResponse({'status': 'ok'})