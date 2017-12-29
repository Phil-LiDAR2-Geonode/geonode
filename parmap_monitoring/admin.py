from django.contrib import admin
from parmap_monitoring.models import DataDownload

class DataDownloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'data_id', 'data_downloaded', 'data_type', 'date_downloaded')
    list_per_page = 50

admin.site.register(DataDownload, DataDownloadAdmin)
