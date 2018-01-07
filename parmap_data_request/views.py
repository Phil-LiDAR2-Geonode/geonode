from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_POST
import simplejson as json

from django.template import RequestContext
from django.shortcuts import render_to_response
from geonode.layers.models import Layer

from geonode.base.models import ResourceBase
from geonode.people.models import Profile
from parmap_data_request.models import DataRequest

from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# add view is invoked via HTTP POST
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

    requested_resource = get_object_or_404(ResourceBase, uuid=request_uuid)
    requestor = Profile.objects.get(username=request.user.username)
    date = timezone.now()
    request_letter_file = "_".join([request.user.username, date.strftime('%Y%m%d'), date.strftime('%H%M%S')]) + ".pdf"
    fs = FileSystemStorage()
    request_letter_path = settings.MEDIA_ROOT + "/data_request/" + request_letter_file
    request_letter_filepath = fs.save(request_letter_path, request_letter)
    site_admin_email = settings.THEME_ACCOUNT_CONTACT_EMAIL

    # i think we should not be catching generic exceptions and instead catching class specific errors
    try:
        data_request = DataRequest(resource=requested_resource, profile=requestor, letter_filename=request_letter_filepath, status='AWAITING')
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

    resource_type = unicode(requested_resource.polymorphic_ctype.model).encode('utf8')
    if resource_type == "layer":
        data_url = settings.SITEURL + 'layers/geonode:' + unicode(requested_resource.layer.name).encode('utf8'),
    else:
        data_url = settings.SITEURL + 'documents/' + unicode(requested_resource.id).encode('utf8'),

    context['data_url'] = data_url

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
    #return HttpResponseRedirect(settings.SITEURL + "documents/")

def test_related(request):
    title_search = 'national_flood_va'
    layer_title = unicode(title_search).encode('utf8')
    layer_resource = get_object_or_404(Layer, title=layer_title)
    resource_keywords = layer_resource.keywords.names()
    
    is_va = False
    if "_va" in layer_resource.typename:
        is_va = True
    
    typename = '_'.join(layer_resource.typename.split(":")[1].split("_")[:2])

    resources = []
    for related_layer in Layer.objects.filter(typename__icontains=typename):
        resources.append(related_layer)

    return render_to_response('parmap_data_request/test_related.html',RequestContext(request, {
        "title": title_search,
        "resource": layer_resource,
        "typename": typename,
        "keywords": resource_keywords,
        "resources": resources,
        "is_va": is_va
    }))