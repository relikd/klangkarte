from django.http import HttpRequest, JsonResponse
from django.urls import path

from app.models.place import Place


def run_tool(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'error': 'unsupported method type'})

    action = request.POST.get('action')

    if action == 'generate-thumbnails':
        Place.recreateThumbnails()
    else:
        return JsonResponse({'error': 'unknown action'})

    return JsonResponse({'success': 'ok'})


urlpatterns = [
    path('tool/', run_tool, name='exec-tool'),
]
