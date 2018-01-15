from django.contrib import admin
from parmap_docs.models import Publication, TechReport

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_uploaded')
    list_per_page = 50

class TechReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'doc_type', 'date_uploaded')
    list_per_page = 50

admin.site.register(Publication, PublicationAdmin)
admin.site.register(TechReport, TechReportAdmin)
