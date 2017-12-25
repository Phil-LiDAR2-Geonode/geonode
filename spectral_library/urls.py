from django.conf.urls import patterns, url

urlpatterns = patterns('spectral_library.views',
                        url(r'^$', 'index', name='index'),
                        url(r'^browse_queue/(?P<target_type>[\w\s]+)/(?P<prov>[\w\s]+)/$', 'browse_queue', name='browse_queue'),
                        url(r'^browse_queue/(?P<targets>[\w\s]+)/$', 'download_files', name='download_files'),
                        url(r'^filter_by_target/(?P<target_type>[\w\s]+)/(?P<prov>[\w\s]+)/$', 'filter_by_target', name='filter_by_target'),
                        url(r'^target/(?P<target_id>\d+)/?$', 'target_detail', name='target_detail'),
                        url(r'^add_to_queue/(?P<target_type>[\w\s]+)/(?P<prov>[\w\s]+)/(?P<targets>[\w\s]+)/$', 'add_to_queue', name='add_to_queue'),
                        url(r'^target/(?P<target_id>\d+)/update_queue/$', 'update_queue', name='update_queue'),
                        url(r'^remove_from_queue/(?P<target_id>\d+)$', 'remove_from_queue', name='remove_from_queue'),
                       )
