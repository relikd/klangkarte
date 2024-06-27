from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import os
import uuid
from pathlib import Path

from common.form.audio_file import AudioFileField


def overwrite_audio(instance: 'Audiofile', filename: str):
    if instance.path.is_file():
        os.remove(instance.path)
    return instance.url


class Audiofile(models.Model):
    key = models.UUIDField('ID', primary_key=True, default=uuid.uuid4,
                           editable=False)
    audio = AudioFileField('Audio', upload_to=overwrite_audio)
    desc = models.CharField('Beschreibung', max_length=200)
    created = models.DateTimeField('Erstellt', auto_now_add=True)

    class Meta:
        verbose_name = 'Audiodatei'
        verbose_name_plural = 'Audiodateien'
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.desc

    @property
    def path(self) -> Path:
        return settings.MEDIA_ROOT / 'audio' / f'{self.pk}.mp3'

    @property
    def url(self) -> str:
        return f'audio/{self.pk}.mp3'


@receiver(post_delete, sender=Audiofile)
def on_delete_Audiofile(sender, instance: 'Audiofile', using, **kwargs):
    os.remove(instance.path)
