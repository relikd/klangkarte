from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import json
from colorfield.fields import ColorField

import typing
if typing.TYPE_CHECKING:
    from app.models.place import Place


class Category(models.Model):
    name = models.CharField('Name', max_length=100)
    color = ColorField('Farbe', default='#3388ff', max_length=7)
    fg_color_white = models.BooleanField('Textfarbe Weiß', default=False)
    sort = models.IntegerField('Sortierung', default=0)

    places: 'models.QuerySet[Place]'

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'
        ordering = ('sort',)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        rv = super().save(*args, **kwargs)
        Category.update_json()
        return rv

    @staticmethod
    def update_json():
        with open(settings.MEDIA_ROOT / 'categories.json', 'w') as fp:
            json.dump(Category.asJson(), fp)

    @staticmethod
    def asJson() -> 'list[dict[str, str]]':
        rv = []
        for x in Category.objects.all():
            rv.append({
                'id': x.pk,
                'name': x.name,
                'color': x.color,
                'inv': x.fg_color_white,
            })
        return rv


@receiver(post_delete, sender=Category)
def on_delete_Category(sender, instance: 'Category', using, **kwargs):
    Category.update_json()
