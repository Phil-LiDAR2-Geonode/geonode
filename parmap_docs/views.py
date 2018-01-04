from django.template import RequestContext, loader
from django.shortcuts import render
from parmap_docs.models import Publication, TechReport
from parmap_monitoring.models import DataDownload
from geonode.people.models import Profile
from django.template import loader
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render_to_response
import os

def publication_list(request):
    publication_list = Publication.objects.order_by('title')
    return render_to_response('parmap_docs/publication_list.html',RequestContext(request, {
        'publication_list': publication_list,}))

def publication_view(request, publication_id):
    # tracking of downloads
    dd = DataDownload()
    dd.username = Profile.objects.get(username=request.user.username)
    dd.email = Profile.objects.get(username=request.user.username).email
    dd.first_name = Profile.objects.get(username=request.user.username).first_name
    dd.last_name = Profile.objects.get(username=request.user.username).last_name
    dd.data_id = publication_id
    dd.data_downloaded = Publication.objects.get(pk=publication_id)
    dd.data_type = "Conference Papers and Publications"
    dd.date_downloaded = timezone.now()
    dd.save()
    # view pdf
    pdf_path = os.path.join(settings.MEDIA_ROOT, str(Publication.objects.get(pk=publication_id).doc_file))
    pdf_file = os.path.basename(pdf_path)
    with open(pdf_path, 'r') as pdf:
        response = HttpResponse(pdf.read(), mimetype='application/pdf')
        response['Content-Disposition'] = 'inline;filename=%s ' % pdf_file
        return response
    pdf.closed
