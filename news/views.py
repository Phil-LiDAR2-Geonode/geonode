from django.template import RequestContext, loader
from news.models import Article
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response

def article_list(request):
    latest_article_list = Article.objects.all().order_by('-pub_date')[:5]
    return render_to_response('news/article_list.html',
        RequestContext(request, {'latest_article_list': latest_article_list}))
