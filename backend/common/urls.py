from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.urls import include, path

from pathlib import Path

from app.models.place import Place


def tinymce_upload(request: HttpRequest, placeId: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'unsupported method type'})

    try:
        Place.objects.get(pk=placeId)
    except Place.DoesNotExist:
        return JsonResponse({'error': 'place does not exist'})

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'could not read file'})

    save_dir = Path(settings.MEDIA_ROOT) / str(placeId)
    if not save_dir.exists():
        save_dir.mkdir()
    with open(save_dir / file.name, 'wb') as fp:
        fp.write(file.read())

    fname = f'{placeId}/{file.name}'
    return JsonResponse({'location': settings.MEDIA_URL + fname})


urlpatterns = [
    path('tinymce/', include('tinymce.urls')),
    path('tinymce/upload/<int:placeId>/', tinymce_upload),
]
