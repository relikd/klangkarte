from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group  # , User
from django.utils.html import format_html

from app.models import Audiofile, Category, Content, Place

# admin.site.register(Place, )

#############################
# Django defaults
#############################

admin.site.site_header = 'Klangkarte-Verwaltung'  # top-most title
admin.site.index_title = 'Klangkarte'  # title at root
admin.site.site_title = 'Klangkarte-Verwaltung'  # suffix to <title>

admin.site.unregister(Group)
# admin.site.unregister(User)


#############################
# App adjustments
#############################


@admin.register(Audiofile)
class AudiofileAdmin(admin.ModelAdmin):
    list_display = ['desc', 'media_url', 'created']
    search_fields = ['desc']

    @admin.display(description='URL')
    def media_url(self, obj: 'Audiofile'):
        return settings.MEDIA_URL + obj.url


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_dot', 'sort', 'places_count']
    search_fields = ['name']

    class Media:
        css = {'all': ['admin/admin.css']}

    @admin.display(description='Orte')
    def places_count(self, obj: 'Category'):
        return obj.places.count()

    @admin.display(description='Farbe')
    def color_dot(self, obj: 'Category'):
        return format_html(
            '<span class="color-dot" style="background:{};color:{}">{}</span>',
            obj.color,
            '#fff' if obj.fg_color_white else '#000',
            obj.color.upper())


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'body']
    search_fields = ['title', 'body']

    def get_readonly_fields(self, request, obj=None):
        return ['key'] if obj else []


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'sort', 'created']
    search_fields = ['title']
    list_filter = ['category']
    change_list_template = 'admin/place_tools.html'
