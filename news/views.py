from django.template import RequestContext, loader
from news.models import Article
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response

def index(request):
    latest_article_list = Article.objects.all().order_by('-pub_date')[:5]
    return render_to_response('news/index.html',
        RequestContext(request, {'latest_article_list': latest_article_list}))

def detail(request, article_id):
    try:
        p = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        raise Http404
    return render_to_response('news/detail.html', RequestContext(request, {'article': p}))

def results(request, article_id):
    return HttpResponse("You're looking at the results of article %s." % article_id)

def vote(request, article_id):
    return HttpResponse("You're voting on article %s." % article_id)
