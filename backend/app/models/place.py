from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import json
import os
import shutil
from pathlib import Path
from PIL import Image, ImageOps
from tinymce.models import HTMLField
from map_location.fields import LocationField

from app.models.category import Category
from common.form.audio_file import AudioFileField
from common.form.img_with_preview import ThumbnailImageField


def overwrite_img_upload(instance: 'Place', filename: str):
    path = instance.fixed_os_path('img.jpg')
    if path.is_file():
        os.remove(path)
    return instance.fixed_save_url('img.jpg')


def overwrite_audio_upload(instance: 'Place', filename: str):
    path = instance.fixed_os_path('audio.mp3')
    if path.is_file():
        os.remove(path)
    return instance.fixed_save_url('audio.mp3')


class Place(models.Model):
    category: 'models.ForeignKey[Category]' = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='places',
        verbose_name='Kategorie')

    sort = models.IntegerField('Sortierung', default=0)
    isExtended = models.BooleanField('Bis 1.1.2025 verstecken')
    title = models.CharField('Titel', max_length=100)
    image = ThumbnailImageField('Bild', blank=True, null=True,
                                upload_to=overwrite_img_upload)  # type: ignore
    audio = AudioFileField('Audio', blank=True, null=True,
                           upload_to=overwrite_audio_upload)
    location = LocationField('Position', blank=True, null=True, options={
        'map': {
            'center': [49.895, 10.890],
            'zoom': 14,
        },
    })
    description = HTMLField('Beschreibung')
    created = models.DateTimeField('Erstellt', auto_now_add=True)

    class Meta:
        verbose_name = 'Ort'
        verbose_name_plural = 'Orte'
        ordering = ('sort',)

    def __str__(self) -> str:
        return self.title

    def fixed_os_path(self, name: str) -> Path:
        return settings.MEDIA_ROOT / str(self.pk) / name

    def fixed_save_url(self, name: str) -> str:
        if self.pk is None:
            next_id = Place.objects.count() + 1
            return f'{next_id}/{name}'
        return f'{self.pk}/{name}'

    @property
    def cover_image_url(self) -> 'str|None':
        if self.image:
            return self.image.url.replace('img.jpg', 'cov.jpg')
        return None

    def save(self, *args, **kwargs):
        rv = super().save(*args, **kwargs)
        self.update_cover_image()
        Place.update_json()
        return rv

    def update_cover_image(self):
        path = self.fixed_os_path('cov.jpg')
        if self.image:
            img = Image.open(self.image.path)
            thumb = ImageOps.fit(img, (600, 400))
            # img.thumbnail((600, 400))
            path.parent.mkdir(parents=True, exist_ok=True)
            thumb.save(path, 'jpeg')
        else:
            if path.exists():
                os.remove(path)

    @staticmethod
    def update_json():
        with open(settings.MEDIA_ROOT / 'places.json', 'w') as fp:
            json.dump(Place.asJson(), fp)

    @staticmethod
    def asJson() -> 'list[dict[str, str]]':
        rv = []
        for x in Place.objects.all():
            rv.append({
                'id': x.pk,
                'name': x.title,
                'loc': [round(x.location.lat, 6),
                        round(x.location.long, 6)] if x.location else None,
                'cat': x.category.pk,
                'cov': x.cover_image_url,
                'img': x.image.url if x.image else None,
                'audio': x.audio.url if x.audio else None,
                'later': x.isExtended,
                'desc': x.description,
            })
        return rv


@receiver(post_delete, sender=Place)
def on_delete_Place(sender, instance: 'Place', using, **kwargs):
    shutil.rmtree(settings.MEDIA_ROOT / str(instance.pk), ignore_errors=True)
    Place.update_json()
