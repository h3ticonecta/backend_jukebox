from django.http import JsonResponse


def index(request):
    return JsonResponse({
        'service': 'backend_jukebox',
        'status': 'running',
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
        },
    })


def health(request):
    return JsonResponse({'status': 'ok'})