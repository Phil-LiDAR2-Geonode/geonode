from django.conf.urls import patterns, url

urlpatterns = patterns('uas.views',
                        url(r'^$', 'index', name='index'),
                        url(r'^browse/(?P<sensor>[\w\s]+)/(?P<resolution>[\w\s]+)/$', 'browse', name='browse'),
                        url(r'^imagery/(?P<imagery_id>\d+)$', 'imagery_detail', name='imagery_detail'),
                        )
