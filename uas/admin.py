from django.contrib import admin
from uas.models import Imagery

class ImageryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sensor', 'resolution')
    list_per_page = 50

admin.site.register(Imagery, ImageryAdmin)
