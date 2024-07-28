# Generated by Django 4.2.13 on 2024-06-22 15:46

import app.models.audiofile
import app.models.place
import colorfield.fields
import common.form.audio_file
import common.form.img_with_preview
import map_location.fields
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Audiofile',
            fields=[
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', common.form.audio_file.AudioFileField(upload_to=app.models.audiofile.overwrite_audio, verbose_name='Audio')),
                ('desc', models.CharField(max_length=200, verbose_name='Beschreibung')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt')),
            ],
            options={
                'verbose_name': 'Audiodatei',
                'verbose_name_plural': 'Audiodateien',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('color', colorfield.fields.ColorField(default='#3388ff', image_field=None, max_length=7, samples=None, verbose_name='Farbe')),
                ('fg_color_white', models.BooleanField(default=False, verbose_name='Textfarbe Weiß')),
                ('sort', models.IntegerField(default=0, verbose_name='Sortierung')),
            ],
            options={
                'verbose_name': 'Kategorie',
                'verbose_name_plural': 'Kategorien',
                'ordering': ('sort',),
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('key', models.SlugField(primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Titel')),
                ('body', tinymce.models.HTMLField(verbose_name='Inhalt')),
                ('wide', models.BooleanField(verbose_name='Breiteres Fenster')),
            ],
            options={
                'verbose_name': 'Text',
                'verbose_name_plural': 'Texte',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort', models.IntegerField(default=0, verbose_name='Sortierung')),
                ('isExtended', models.BooleanField(verbose_name='Bis 1.1.2025 verstecken')),
                ('title', models.CharField(max_length=100, verbose_name='Titel')),
                ('image', common.form.img_with_preview.ThumbnailImageField(blank=True, null=True, upload_to=app.models.place.overwrite_img_upload, verbose_name='Bild')),
                ('audio', common.form.audio_file.AudioFileField(blank=True, null=True, upload_to=app.models.place.overwrite_audio_upload, verbose_name='Audio')),
                ('location', map_location.fields.LocationField(blank=True, null=True, verbose_name='Position')),
                ('description', tinymce.models.HTMLField(verbose_name='Beschreibung')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='app.category', verbose_name='Kategorie')),
            ],
            options={
                'verbose_name': 'Ort',
                'verbose_name_plural': 'Orte',
                'ordering': ('sort',),
            },
        ),
    ]
