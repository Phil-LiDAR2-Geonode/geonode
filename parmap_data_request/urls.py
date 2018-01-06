from django.conf import settings, urls
from parmap_data_request.views import handle_upload, test_related

urlpatterns = urls.patterns('',
    urls.url(r'^add/$', handle_upload, name='datarequest_add'),
    urls.url(r'^test_related/$', test_related, name='test_related'),
)
