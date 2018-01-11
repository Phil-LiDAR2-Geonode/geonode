from django.template import RequestContext, loader
from spectral_library.models import Target, Queue
from geonode.people.models import Profile
from parmap_monitoring.models import DataDownload
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
import os
import zipfile
import StringIO
from django.utils.translation import ugettext as _


def index(request):
    target_list = Target.objects.order_by('common_name').distinct('common_name')
    return render_to_response('spectral_library/search_index.html',RequestContext(request, {'target_list': target_list,}))

def filter_by_target(request, target_type, prov):
    target_list = Target.objects.order_by('common_name').distinct('common_name')
    prov_list = Target.objects.order_by('province').distinct('province')
    try:
        user = Profile.objects.get(username=request.user.username)
        queue_list = Queue.objects.filter(profile=user).order_by('target')
    except:
        queue_list = None

    if target_type == "all" and prov != "all":
        target_results = Target.objects.filter(province=prov.title()).order_by('title')
    elif target_type != "all" and prov == "all":
        target_results = Target.objects.filter(common_name=target_type.title()).order_by('title')
    elif target_type != "all" and prov != "all":
        target_results =  Target.objects.filter(common_name=target_type.title()).filter(province=prov.title()).order_by('title')
    else:
        target_results = Target.objects.order_by('title')

    return render_to_response('spectral_library/target_filter_results.html',RequestContext(request, {
        'target_list': target_list,
        'prov_list': prov_list,
        'target_results': target_results,
        'target_type': target_type.title(),
        'prov_name': prov.title(),
        'queue_list': queue_list,
        }))

def target_detail(request, target_id):
    target_list = Target.objects.order_by('common_name').distinct('common_name')
    prov_list = Target.objects.order_by('province').distinct('province')
    target = Target.objects.get(pk=target_id)
    try:
        user = Profile.objects.get(username=request.user.username)
        queue_list = Queue.objects.filter(profile=user).order_by('target')
    except:
        queue_list = None

    return render_to_response('spectral_library/target_detail.html', RequestContext(request, {
        'target_list': target_list,
        'prov_list': prov_list,
        'target': target,
        'queue_list': queue_list,
        }))

def add_to_queue(request, target_type, prov, targets):
    target_list = targets.split()
    user = Profile.objects.get(username=request.user.username)
    for target_name in target_list:
        target = Target.objects.get(pk=target_name)
        q = Queue(profile_id=user.id, target_id=target.id)
        q.save()
    return redirect(filter_by_target, target_type = target_type, prov = prov)

def update_queue(request, target_id):
    user = Profile.objects.get(username=request.user.username)
    target = Target.objects.get(pk=target_id)
    q = Queue(profile_id=user.id, target_id=target.id)
    q.save()
    return redirect(target_detail, target_id = target.id)

def remove_from_queue(request, target_id):
    user = Profile.objects.get(username=request.user.username)
    target = Target.objects.get(pk=target_id)
    q = Queue.objects.filter(profile_id=user.id, target_id=target.id)
    q.delete()
    return redirect(browse_queue)

def browse_queue(request):
    targets = Target.objects.order_by('common_name')
    target_list = Target.objects.order_by('common_name').distinct('common_name')
    prov_list = Target.objects.order_by('province').distinct('province')
    user = Profile.objects.get(username=request.user.username)
    queue_list = Queue.objects.filter(profile=user).order_by('target')

    return render_to_response('spectral_library/browse_queue.html',RequestContext(request, {
        'targets': targets,
        'target_list': target_list,
        'prov_list': prov_list,
        'queue_list': queue_list,
        }))

def download_files(request, targets):
    try:
        target_list = targets.split()

        date = timezone.now()
        zip_subdir = "_".join(["spectro", request.user.username, date.strftime('%Y%m%d'), date.strftime('%H%M%S')])
        zip_filename = "%s.zip" % zip_subdir

        s = StringIO.StringIO()

        zf = zipfile.ZipFile(s, "w")

        for target_id in target_list:
            target_path = os.path.join(settings.MEDIA_ROOT, str(Target.objects.get(pk=target_id).target_file))
            fdir, fname = os.path.split(target_path)
            zip_path = os.path.join(zip_subdir, fname)

            zf.write(target_path, zip_path)
            # tracking of downloads
            dd = DataDownload()
            dd.username = Profile.objects.get(username=request.user.username)
            dd.email = Profile.objects.get(username=request.user.username).email
            dd.first_name = Profile.objects.get(username=request.user.username).first_name
            dd.last_name = Profile.objects.get(username=request.user.username).last_name
            dd.data_id = target_id
            dd.data_downloaded = Target.objects.get(pk=target_id)
            dd.data_type = "Spectral Signature"
            dd.date_downloaded = timezone.now()
            dd.save()

        zf.close()

        resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

        user = Profile.objects.get(username=request.user.username)
        q = Queue.objects.filter(profile_id=user.id)
        q.delete()

        return resp
    except:
        return HttpResponse(
            loader.render_to_string(
                '401.html', RequestContext(
                    request, {
                        'error_message': _("You are not allowed to download this data.")})), status=403)

def download(request, target_id):
    try:
        # tracking of downloads
        dd = DataDownload()
        dd.username = Profile.objects.get(username=request.user.username)
        dd.email = Profile.objects.get(username=request.user.username).email
        dd.first_name = Profile.objects.get(username=request.user.username).first_name
        dd.last_name = Profile.objects.get(username=request.user.username).last_name
        dd.data_id = target_id
        dd.data_downloaded = Target.objects.get(pk=target_id)
        dd.data_type = "Spectral Signature"
        dd.date_downloaded = timezone.now()
        dd.save()
        # download zipped file
        target_path = os.path.join(settings.MEDIA_ROOT, str(Target.objects.get(pk=target_id).target_file))
        target_file = os.path.basename(target_path)
        fp = open(target_path, 'rb')
        response = HttpResponse(fp.read())
        fp.close()
        response['content_type'] = "application/x-zip-compressed"
        response['Content-Disposition'] = 'attachment;filename=%s ' % target_file
        return response
    except:
        return HttpResponse(
            loader.render_to_string(
                '401.html', RequestContext(
                    request, {
                        'error_message': _("You are not allowed to download this data.")})), status=403)
