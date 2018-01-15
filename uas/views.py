from django.template import RequestContext, loader
from uas.models import Imagery, UASRequest
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
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import simplejson as json

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
    approved_status = False
    pending_status = False
    if request.user.is_authenticated():
        try:
            pending_request = UASRequest.objects.filter(profile=request.user).get(resource=imagery_id)
            if pending_request.status != 'APPROVED':
                pending_status = True
            elif pending_request.status == 'APPROVED':
                approved_status = True
        except UASRequest.DoesNotExist:
            pending_status = False
        except DataRequest.MultipleObjectsReturned:
            pending_status = True
    return render_to_response('uas/imagery_detail.html',RequestContext(request, {
        'imagery': imagery,
        'has_pending_request': pending_status,
        'is_request_approved': approved_status
        }))

def download(request, imagery_id):
    try:
        uas_request = UASRequest.objects.filter(profile=request.user).get(resource=imagery_id)
        if uas_request.status == "APPROVED":
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
        else:
            return HttpResponse(
                loader.render_to_string(
                    '401.html', RequestContext(
                        request, {
                            'error_message': _("You are not allowed to download this data.")})), status=403)
    except:
        return HttpResponse(
            loader.render_to_string(
                '401.html', RequestContext(
                    request, {
                        'error_message': _("You are not allowed to download this data.")})), status=403)

@require_POST
def handle_upload(request):
    response = ""

    if not request.user.is_authenticated():
        # return HttpResponse(status=403)
        response = "User is not authorized"

    request_letter = request.FILES.get('letter_file')
    if not request_letter:
        # return HttpResponse(status=400)
        response = "Missing request letter"

    request_uuid = request.POST.get('uuid')
    if not request_uuid:
        #return HttpResponse(status=400)
        response = "Missing resource UUID"

    requested_resource = Imagery.objects.get(pk=request_uuid)
    requestor = Profile.objects.get(username=request.user.username)
    date = timezone.now()
    request_letter_file = "_".join([request.user.username, date.strftime('%Y%m%d'), date.strftime('%H%M%S')]) + ".pdf"
    fs = FileSystemStorage()
    request_letter_path = settings.MEDIA_ROOT + "/uas_request/" + request_letter_file
    request_letter_filepath = fs.save(request_letter_path, request_letter)
    site_admin_email = settings.THEME_ACCOUNT_CONTACT_EMAIL

    # i think we should not be catching generic exceptions and instead catching class specific errors
    try:
        data_request = UASRequest(resource=requested_resource, profile=requestor, letter_filename=request_letter_filepath, status='AWAITING')
        data_request.save()
    except Exception as e:
        # @todo, put this on a error log handler
        response = "A problem had occurred on our end, please try again"
        print('There was an error saving to database: ', e)

    if not data_request:
        response = "A problem had occurred on our end, please try again"
        #return HttpResponse(status=500)

    # reusing the same connection
    # uses SMTP server specified in settings.py
    connection = get_connection()
    # If you don't open the connection manually, Django will automatically open,
    # then tear down the connection in msg.send()
    connection.open()

    # needed for template rendering
    context = {
        'site_url': settings.SITEURL,
        'data_requestor': unicode(requestor.get_full_name()).encode('utf8'),
        'data_resource': unicode(requested_resource.title).encode('utf8'),
        'site_admin_email': site_admin_email,
    }

    context['data_url'] = settings.SITEURL + 'uas/imagery/' + request_uuid

    # we send notification of received request to requestor
    subject = 'Notification of Received Request'
    html_content = render_to_string('parmap_data_request/email_notification_received_request.html', context)
    # this strips the html, so people will have the text as well.
    text_content = strip_tags(html_content)

    # convert requestor email address information as string
    recipient = unicode(requestor.email).encode('utf8')
    recipients = [recipient]

    try:
        # create the email, and attach the HTML version as well.
        message_to_requestor = EmailMultiAlternatives(subject, text_content, site_admin_email, recipients)
        message_to_requestor.attach_alternative(html_content, "text/html")
        message_to_requestor.send()

    except Exception as e:
        # @todo, put this on a error log handler
        print('There was an error sending an email to data requestor: ', e)
        response = "A problem had occurred on our end, please try again"

    # we send notification of admin/site owners as well
    subject = 'Data Request Notification'
    html_content = render_to_string('parmap_data_request/email_resource_request.html', context)
    text_content = strip_tags(html_content)
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = [site_admin_email]

    try:
        message_to_requestor = EmailMultiAlternatives(subject, text_content, sender, recipients)
        message_to_requestor.attach_alternative(html_content, "text/html")
        message_to_requestor.send()

    except Exception as e:
        # @todo, put this on a error log handler
        print('There was an error sending an email to site admin: ', e)
        response = "A problem had occurred on our end, please try again"

    # Cleanup
    connection.close()

    data = {}
    if response != "":
        data['error'] = response
    response_data = json.dumps(data)

    # django >1.6.x
    #return HttpResponse(data, content_type='application/json')

    # django 1.6.x
    return HttpResponse(response_data, mimetype='application/json')
