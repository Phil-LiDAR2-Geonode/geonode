from django.contrib import admin
from spectral_library.models import Target, Queue

class TargetAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'province', 'common_name')
    list_per_page = 50

class QueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'target', 'status', 'date_updated')
    list_per_page = 50

admin.site.register(Target, TargetAdmin)
admin.site.register(Queue, QueueAdmin)
