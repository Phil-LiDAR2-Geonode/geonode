from django.conf import settings, urls
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'', views.article_list),
    ]
