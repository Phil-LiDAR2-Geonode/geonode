from django.conf.urls import patterns, url

urlpatterns = patterns('parmap_docs.views',
                        url(r'^publication/$', 'browse_publication', name='browse_publication'),
                        # url(r'^publication/(?P<publication_id>\d+)/?$', 'publication_detail', name='publication_detail'),
                        # url(r'^publication/(?P<publication_id>\d+)/download/$', 'download', name='download'),
                        # url(r'^techreport/(?P<techreport_type>[\w\s]+)/$', 'browse_techreport', name='browse_techreport'),
                        # url(r'^techreport/(?P<techreport_id>\d+)/?$', 'techreport_detail', name='techreport_detail'),
                        # url(r'^techreport/(?P<techreport_id>\d+)/download/$', 'download', name='download'),
                       )
