from django.conf.urls import patterns, url

urlpatterns = patterns('parmap.views',
                        url(r'^other_rs/(?P<facettype>[^/]*)$', 'other_rs', name='other_rs'),
                        url(r'^other_rs/links/(?P<facettype>[^/]*)/(?P<layername>[^/]*)$', 'rs_links', name='rs_links'),
                       )


                       