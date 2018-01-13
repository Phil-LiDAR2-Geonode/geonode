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
        'publication_list': publication_list,
        }))

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
        response['Content-Disposition'] = 'inline;filename=%s ' % pdf_file.replace(",","_")
        return response
    pdf.closed

def techreport_list(request, techreport_type):
    doctype_list = TechReport.objects.order_by('doc_type').distinct('doc_type')
    if techreport_type == "all":
        techreport_list = TechReport.objects.order_by('title')
    elif techreport_type == "field validation manuals":
        techreport_type = "Algorithms/Workflows and Field Validation Manuals"
        techreport_list =  TechReport.objects.filter(doc_type="Algorithms/Workflows and Field Validation Manuals").order_by('title')
    elif techreport_type == "web gis":
        techreport_type = "Operational Web-based GIS Platform"
        techreport_list =  TechReport.objects.filter(doc_type="Operational Web-based GIS Platform").order_by('title')
    elif techreport_type == "qa documentation":
        techreport_type = "QA/QC Documentation"
        techreport_list =  TechReport.objects.filter(doc_type="QA/QC Documentation").order_by('title')
    else:
        techreport_type = techreport_type.title()
        techreport_list =  TechReport.objects.filter(doc_type=techreport_type.title()).order_by('title')
    return render_to_response('parmap_docs/techreport_list.html',RequestContext(request, {
        'techreport_list': techreport_list,
        'techreport_type': techreport_type,
        'doctype_list': doctype_list,
        }))

def techreport_view(request, techreport_id):
    # tracking of downloads
    dd = DataDownload()
    dd.username = Profile.objects.get(username=request.user.username)
    dd.email = Profile.objects.get(username=request.user.username).email
    dd.first_name = Profile.objects.get(username=request.user.username).first_name
    dd.last_name = Profile.objects.get(username=request.user.username).last_name
    dd.data_id = techreport_id
    dd.data_downloaded = TechReport.objects.get(pk=techreport_id)
    dd.data_type = "Technical Reports and Manuals"
    dd.date_downloaded = timezone.now()
    dd.save()
    # view pdf
    pdf_path = os.path.join(settings.MEDIA_ROOT, str(TechReport.objects.get(pk=techreport_id).doc_file))
    pdf_file = os.path.basename(pdf_path)
    with open(pdf_path, 'r') as pdf:
        response = HttpResponse(pdf.read(), mimetype='application/pdf')
        response['Content-Disposition'] = 'inline;filename=%s ' % pdf_file.replace(",","_")
        return response
    pdf.closed
