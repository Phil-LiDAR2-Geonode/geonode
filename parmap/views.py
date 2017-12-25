from django.http import HttpResponse
import json
from django.shortcuts import render
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

from django.conf import settings
from django.utils.translation import ugettext as _
from geonode.services.models import Service
from geonode.utils import resolve_object
from geonode.layers.models import Layer
from geonode.documents.models import Document
from django.utils import timezone
import os
import zipfile
import StringIO

_PERMISSION_MSG_GENERIC = _('You do not have permissions for this layer.')
_PERMISSION_MSG_VIEW = _("You are not permitted to view this layer")

def _resolve_layer(request, typename, permission='base.view_resourcebase',
                   msg=_PERMISSION_MSG_GENERIC, **kwargs):
    """
    Resolve the layer by the provided typename (which may include service name) and check the optional permission.
    """
    service_typename = typename.split(":", 1)

    if Service.objects.filter(name=service_typename[0]).exists():
        service = Service.objects.filter(name=service_typename[0])
        return resolve_object(request,
                              Layer,
                              {'service': service[0],
                               'typename': service_typename[1] if service[0].method != "C" else typename},
                              permission=permission,
                              permission_msg=msg,
                              **kwargs)
    else:
        return resolve_object(request,
                              Layer,
                              {'typename': typename,
                               'service': None},
                              permission=permission,
                              permission_msg=msg,
                              **kwargs)

# Create your views here.
def other_rs(request, facettype='layers'):
    if(facettype == 'layers'):
        queryset = Layer.objects.distinct().filter(typename__icontains='parmap').order_by('-date')[:5]
    else:
        queryset = Document.objects.distinct().filter(title__icontains='Land Cover Map').order_by('-date')[:5]


    context_dict = {
        "list": queryset,
        "facettype": facettype,
        "map_type": 'rs'
    }
    
    return render_to_response('parmap/other_rs.html', RequestContext(request, context_dict))


def _resolve_document(request, docid, permission='base.change_resourcebase',
                      msg=_PERMISSION_MSG_GENERIC, **kwargs):
    '''
    Resolve the document by the provided primary key and check the optional permission.
    '''
    return resolve_object(request, Document, {'pk': docid},
                          permission=permission, permission_msg=msg, **kwargs)


def rs_links_layers(request, layername):
    layer = _resolve_layer(
        request,
        layername,
        'base.view_resourcebase',
        _PERMISSION_MSG_VIEW)

    config = layer.attribute_config()
    
    if request.user.is_authenticated():
        if layer.storeType == 'dataStore':
            links = layer.link_set.download().filter(
                name__in=settings.DOWNLOAD_FORMATS_VECTOR)
        else:
            links = layer.link_set.download().filter(
                name__in=settings.DOWNLOAD_FORMATS_RASTER)
    else:
        links = []

    context_dict = {
        "facettype": "layers",
        "layername": layername,
        "links": links
    }
    
    return render_to_response('parmap/rs_links.html', RequestContext(request, context_dict))


def rs_download_layers(request):
    queue = request.POST['queue']
    print queue
    return HttpResponse(json.dumps(queue),mimetype='application/json',status=200)

def rs_download_maps(request):
    queue = dict(request.POST)["queue"]
    
    date = timezone.now()
    zip_subdir = "_".join(["spectro", request.user.username, date.strftime('%Y%m%d'), date.strftime('%H%M%S')])
    zip_filename = "%s.zip" % zip_subdir

    s = StringIO.StringIO()

    zf = zipfile.ZipFile(s, "w")

    for docid in queue:
        document = Document.objects.get(id=docid)
        target_path = os.path.join(settings.MEDIA_ROOT, str(document.doc_file))
        fdir, fname = os.path.split(target_path)
        zip_path = os.path.join(zip_subdir, fname)

        zf.write(target_path, zip_path)

    zf.close()

    print s.getvalue()

    return HttpResponse(json.dumps(queue),mimetype='application/json',status=200)