from django.conf.urls import patterns, url

urlpatterns = patterns('parmap_docs.views',
                        url(r'^publication/$', 'publication_list', name='publication_list'),
                        url(r'^publication/(?P<publication_id>\d+)/?$', 'publication_view', name='publication_view'),
                        # url(r'^publication/(?P<publication_id>\d+)/download/$', 'download', name='download'),
                        # url(r'^techreport/(?P<techreport_type>[\w\s]+)/$', 'browse_techreport', name='browse_techreport'),
                        # url(r'^techreport/(?P<techreport_id>\d+)/?$', 'techreport_detail', name='techreport_detail'),
                        # url(r'^techreport/(?P<techreport_id>\d+)/download/$', 'download', name='download'),
                       )
