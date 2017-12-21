from django.conf.urls import patterns, url

urlpatterns = patterns('parmap.views',
                        url(r'^other_rs/(?P<facettype>[^/]*)$', 'other_rs', name='other_rs'),
                        url(r'^other_rs/links/layers/(?P<layername>[^/]*)$', 'rs_links_layers', name='rs_links_layers'),
                        url(r'^other_rs/links/maps/(?P<mapname>[^/]*)$', 'rs_links_maps', name='rs_links_maps'),
                       )


                       