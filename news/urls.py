from django.conf.urls import patterns, url

urlpatterns = patterns('news.views',
                        url(r'^$', 'article_list', name='article_list'),
                        url(r'^article/(?P<article_id>\d+)/?$', 'article_detail', name='article_detail'),
                        url(r'^headline/(?P<headline_id>\d+)/?$', 'headline_detail', name='headline_detail'),
                       )
