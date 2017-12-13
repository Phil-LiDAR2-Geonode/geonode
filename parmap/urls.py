from django.conf.urls import patterns, url

urlpatterns = patterns('parmap.views',
                        url(r'^other_rs/(?P<facettype>[^/]*)$', 'other_rs', name='other_rs'),
                       )


                       