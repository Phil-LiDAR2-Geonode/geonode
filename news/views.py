from django.template import RequestContext, loader
from news.models import Article
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response

def article_list(request):
    latest_article_list = Article.objects.all().order_by('-start_date')
    latest_headline = Article.objects.filter(is_headline='True').order_by('-creation_date')[0]
    year_list = Article.objects.dates('start_date','year', order='DESC')
    month_list = Article.objects.dates('start_date','month',order='DESC')
    return render_to_response('news/article_list.html', RequestContext(request, {
        'latest_article_list': latest_article_list,
        'year_list': year_list,
        'month_list' : month_list,
        'latest_headline': latest_headline
        }))

def article_detail(request, article_id):
    article = Article.objects.get(pk=article_id)
    year_list = Article.objects.dates('start_date','year', order='DESC')
    month_list = Article.objects.dates('start_date','month',order='DESC')
    return render_to_response('news/article_detail.html', RequestContext(request, {
        'year_list': year_list,
        'month_list' : month_list,
        'article': article
        }))

def headline_detail(request, headline_id):
    headline = Article.objects.get(pk=headline_id)
    year_list = Article.objects.dates('start_date','year', order='DESC')
    month_list = Article.objects.dates('start_date','month',order='DESC')
    return render_to_response('news/headline_detail.html', RequestContext(request, {
        'year_list': year_list,
        'month_list' : month_list,
        'headline': headline
        }))

def article_list_filter(request, pub_year, pub_month):
    latest_article_list = Article.objects.filter(start_date__year=pub_year, start_date__month=pub_month)
    latest_headline = Article.objects.all().order_by('-creation_date')[0]
    year_list = Article.objects.dates('start_date','year', order='DESC')
    month_list = Article.objects.dates('start_date','month',order='DESC')
    return render_to_response('news/article_results.html', RequestContext(request, {
        'latest_article_list': latest_article_list,
        'year_list': year_list,
        'month_list' : month_list,
        'latest_headline': latest_headline
        }))
