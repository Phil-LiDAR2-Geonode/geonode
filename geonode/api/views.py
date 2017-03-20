from django.shortcuts import (
    redirect, get_object_or_404, render, render_to_response)
from django.http import HttpResponse, HttpResponseRedirect

import urllib2
from django.core.urlresolvers import resolve
import json
from urlparse import urljoin
from urllib2 import HTTPError
from geonode.layers.models import Layer

def total_count(request, apiname):
    output = {}
    output['total_count'] = Layer.objects.all().count()
    return HttpResponse(json.dumps(output),mimetype='application/json',status=200)
