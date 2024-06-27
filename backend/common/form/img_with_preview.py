from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import FileInput, widgets

from common.validators import MaxFilesizeValidator, readableToInt

MAX_UPLOAD_SIZE = '312 KB'


class ImageFileWidget(widgets.ClearableFileInput):
    template_name = 'forms/img-with-preview.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class ImgField(forms.FileField):
    widget = ImageFileWidget
    default_validators = [
        FileExtensionValidator(['jpg', 'jpeg', 'png']),
        MaxFilesizeValidator(MAX_UPLOAD_SIZE),
    ]

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if isinstance(widget, FileInput) and 'accept' not in widget.attrs:
            attrs.setdefault('accept', 'image/png,image/jpeg')  # image/*
        if isinstance(widget, ImageFileWidget):
            attrs.update({
                'data-upload-limit': readableToInt(MAX_UPLOAD_SIZE),
                'data-upload-limit-str': MAX_UPLOAD_SIZE,
                'onchange': 'validate_upload_limit(this)',
            })
        return attrs


class FileWithImagePreview(models.FileField):  # use ImageField to omit Pillow
    __del_image_on_save = False

    def formfield(self, **kwargs):
        if kwargs['widget'] is AdminFileWidget:
            # Override admin widget. Defined by ImgField anyway
            del kwargs['widget']
        return super().formfield(**{'form_class': ImgField, **kwargs})

    def save_form_data(self, instance, data):
        if data is False:
            self.__del_image_on_save = True
        super().save_form_data(instance, data)

    def pre_save(self, model_instance, add):
        if self.__del_image_on_save:
            self.__del_image_on_save = False
            self.deletePreviousImage(model_instance)
        return super().pre_save(model_instance, add)

    def deletePreviousImage(self, instance: models.Model):
        if not instance.pk:
            return
        prev = instance.__class__.objects.get(pk=instance.pk)
        imgField = getattr(prev, self.attname)
        imgField.delete(save=False)
