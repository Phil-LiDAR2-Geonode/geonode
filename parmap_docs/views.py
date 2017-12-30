from django.template import RequestContext, loader
from django.shortcuts import render
from parmap_docs.models import Publication, TechReport
from geonode.people.models import Profile
from django.template import loader
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render_to_response
import os

def browse_publication(request):
    publication_list = Publication.objects.order_by('title')
    return render_to_response('parmap_docs/browse_publication.html',RequestContext(request, {'publication_list': publication_list,}))
