from django.template import RequestContext, loader
from news.models import Article
from news.models import Headline
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response

def article_list(request):
    latest_article_list = Article.objects.all().order_by('-pub_date')[:5]
    latest_headline = Headline.objects.all().order_by('-pub_date')[0]
    return render_to_response('news/article_list.html',
        RequestContext(request, {'latest_article_list': latest_article_list}),
        RequestContext(request, {'latest_headline': latest_headline}))

def article_detail(request, article_id):
    try:
        a = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        raise Http404
    return render_to_response('news/article_detail.html', RequestContext(request, {'article': a}))

def headline_detail(request, headline_id):
    try:
        h = Headline.objects.get(pk=headline_id)
    except Headline.DoesNotExist:
        raise Http404
    return render_to_response('news/headline_detail.html', RequestContext(request, {'headline': h}))

def article_list_filter(request, pub_year, pub_month):
    latest_article_list = Article.objects.filter(pub_date__year=pub_year, pub_date__month=pub_month)
    latest_headline = Headline.objects.all().order_by('-pub_date')[0]
    return render_to_response('news/article_list.html',
        RequestContext(request, {'latest_article_list': latest_article_list}),
        RequestContext(request, {'latest_headline': latest_headline}))
