from django.conf.urls import patterns, url

urlpatterns = patterns('parmap_monitoring.views',
                        url(r'^$', 'export_to_csv', name='export_to_csv'),
                        )
