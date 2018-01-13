from django.conf.urls import patterns, url

urlpatterns = patterns('parmap_docs.views',
                        url(r'^publication/$', 'publication_list', name='publication_list'),
                        url(r'^publication/(?P<publication_id>\d+)/?$', 'publication_view', name='publication_view'),
                        url(r'^techreport/(?P<techreport_type>[\w\s]+)/$', 'techreport_list', name='techreport_list'),
                        url(r'^techreport/(?P<techreport_id>\d+)/?$', 'techreport_view', name='techreport_view'),
                       )
