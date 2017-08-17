from django.conf import settings, urls
from parmap_data_request.views import handle_upload

urlpatterns = urls.patterns('',
    urls.url(r'^add/$', handle_upload, name='datarequest_add'),
)
