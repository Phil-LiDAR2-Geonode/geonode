from django.conf.urls import patterns, url

urlpatterns = patterns('news.views',
                        url(r'^$', 'article_list', name='article_list'),
                        url(r'^(?P<article_id>\d+)/?$', 'article_detail', name='article_detail'),
                       )
