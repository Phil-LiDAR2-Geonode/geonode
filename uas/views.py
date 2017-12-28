from django.template import RequestContext, loader
from uas.models import Imagery
from geonode.people.models import Profile
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render

def index(request):
    return render(request, 'uas/uas_index.html')

def browse(request, sensor, resolution):
    if resolution == "null" and sensor == "null":
        imagery_results =  []
    elif resolution == "all" and sensor != "all":
        imagery_results = Imagery.objects.filter(sensor=sensor.upper()).order_by('title')
    elif resolution != "all" and sensor == "all":
        imagery_results = Imagery.objects.filter(resolution=resolution).order_by('title')
    elif resolution != "all" and sensor != "all":
        imagery_results =  Imagery.objects.filter(resolution=resolution).filter(sensor=sensor.upper()).order_by('title')
    else:
        imagery_results = Imagery.objects.order_by('title')

    return render_to_response('uas/imagery_browse.html',RequestContext(request, {
        'resolution': resolution.upper(),
        'sensor': sensor.upper(),
        'imagery_results': imagery_results,
        }))

def imagery_detail(request, imagery_id):
    imagery = Imagery.objects.get(pk=imagery_id)
    return render_to_response('uas/imagery_detail.html',RequestContext(request, {
        'imagery': imagery,
        }))
