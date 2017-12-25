from django.contrib import admin
from api_static.models import Filter

class FilterAdmin(admin.ModelAdmin):
    list_display = ('filter', 'type', 'label')
    list_per_page = 50

admin.site.register(Filter, FilterAdmin)
