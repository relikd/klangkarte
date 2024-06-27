from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import FileInput, widgets

from common.validators import MaxFilesizeValidator, readableToInt

MAX_UPLOAD_SIZE = '20 MB'


class AudioFileWidget(widgets.ClearableFileInput):
    template_name = 'forms/audio-file.html'

    class Media:
        js = ['admin/file-upload-validator.js']

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class AudioField(forms.FileField):
    widget = AudioFileWidget
    default_validators = [
        FileExtensionValidator(['mp3']),
        MaxFilesizeValidator(MAX_UPLOAD_SIZE)
    ]

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if isinstance(widget, FileInput) and 'accept' not in widget.attrs:
            attrs.setdefault('accept', 'audio/mpeg')  # audio/*
        if isinstance(widget, AudioFileWidget):
            attrs.update({
                'data-upload-limit': readableToInt(MAX_UPLOAD_SIZE),
                'data-upload-limit-str': MAX_UPLOAD_SIZE,
                'onchange': 'validate_upload_limit(this)',
            })
        return attrs


class AudioFileField(models.FileField):
    __del_file_on_save = False

    def formfield(self, **kwargs):
        if kwargs['widget'] is AdminFileWidget:
            # Override admin widget. Defined by AudioField anyway
            del kwargs['widget']
        return super().formfield(**{'form_class': AudioField, **kwargs})

    def save_form_data(self, instance, data):
        if data is False:
            self.__del_file_on_save = True
        super().save_form_data(instance, data)

    def pre_save(self, model_instance, add):
        if self.__del_file_on_save:
            self.__del_file_on_save = False
            self.deletePreviousFile(model_instance)
        return super().pre_save(model_instance, add)

    def deletePreviousFile(self, instance: models.Model):
        if not instance.pk:
            return
        prev = instance.__class__.objects.get(pk=instance.pk)
        fileField = getattr(prev, self.attname)
        fileField.delete(save=False)
