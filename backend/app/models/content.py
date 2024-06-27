from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

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
        Content.update_json()
        return rv

    @staticmethod
    def update_json():
        with open(settings.MEDIA_ROOT / 'text.json', 'w') as fp:
            json.dump(Content.asJson(), fp)

    @staticmethod
    def asJson() -> 'dict[str, str]':
        rv = {}
        for x in Content.objects.all():
            rv[x.pk] = {'title': x.title, 'body': x.body, 'wide': x.wide}
        return rv


@receiver(post_delete, sender=Content)
def on_delete_Content(sender, instance: 'Content', using, **kwargs):
    Content.update_json()
