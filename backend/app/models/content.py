from django.conf import settings
from django.db import models

import json
from tinymce.models import HTMLField


class Content(models.Model):
    key = models.SlugField('ID', primary_key=True, unique=True)
    title = models.CharField('Titel', max_length=100)
    body = HTMLField('Inhalt')
    wide = models.BooleanField('Breiteres Fenster')

    class Meta:
        verbose_name = 'Text'
        verbose_name_plural = 'Texte'

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        rv = super().save(*args, **kwargs)
        self.update_json()
        return rv

    def delete(self, *args, **kwargs):
        rv = super().delete(*args, **kwargs)
        self.update_json()
        return rv

    def update_json(self):
        with open(settings.MEDIA_ROOT / 'text.json', 'w') as fp:
            json.dump(self.asJson(), fp)

    @staticmethod
    def asJson() -> 'dict[str, str]':
        rv = {}
        for x in Content.objects.all():
            rv[x.pk] = {'title': x.title, 'body': x.body, 'wide': x.wide}
        return rv
