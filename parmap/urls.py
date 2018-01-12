from django.conf.urls import patterns, url

urlpatterns = patterns('parmap.views',
                        url(r'^other_rs/(?P<facettype>[^/]*)$', 'other_rs', name='other_rs'),
                        url(r'^other_rs/page/(?P<facettype>[^/]*)$', 'other_rs_page', name='other_rs_page'),
                        url(r'^other_rs/queue/(?P<facettype>[^/]*)$', 'other_rs_queue', name='other_rs_queue'),
                        url(r'^other_rs/links/layers/(?P<layername>[^/]*)$', 'rs_links_layers', name='rs_links_layers'),
                        url(r'^other_rs/download/layers', 'rs_download_layers', name='rs_download_layers'),
                        url(r'^other_rs/download/maps', 'rs_download_maps', name='rs_download_maps')
                       )


                       