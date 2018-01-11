from django.template import RequestContext, loader
from uas.models import Imagery
from parmap_monitoring.models import DataDownload
from geonode.people.models import Profile
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
import os
from django.utils.translation import ugettext as _


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

def download(request, imagery_id):
    try:
        # tracking of downloads
        dd = DataDownload()
        dd.username = Profile.objects.get(username=request.user.username)
        dd.email = Profile.objects.get(username=request.user.username).email
        dd.first_name = Profile.objects.get(username=request.user.username).first_name
        dd.last_name = Profile.objects.get(username=request.user.username).last_name
        dd.data_id = imagery_id
        dd.data_downloaded = Imagery.objects.get(pk=imagery_id)
        dd.data_type = "UAS Imagery"
        dd.date_downloaded = timezone.now()
        dd.save()
        # download zipped file
        imagery_path = os.path.join(settings.MEDIA_ROOT, str(Imagery.objects.get(pk=imagery_id).zipped_file))
        imagery_file = os.path.basename(imagery_path)
        fp = open(imagery_path, 'rb')
        response = HttpResponse(fp.read())
        fp.close()
        response['content_type'] = "application/x-zip-compressed"
        response['Content-Disposition'] = 'attachment;filename=%s ' % imagery_file
        return response
    except:
        return HttpResponse(
            loader.render_to_string(
                '401.html', RequestContext(
                    request, {
                        'error_message': _("You are not allowed to download this data.")})), status=403)
