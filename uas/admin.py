from django.contrib import admin
from uas.models import Imagery, UASRequest
from uas.forms import UASRequestForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from parmap_data_request.models import RequestReason

class ImageryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sensor', 'resolution')
    list_per_page = 50

class UASRequestAdmin(admin.ModelAdmin):
    form = UASRequestForm
    list_display = ('resource', 'profile', 'date_created', 'status')
    list_per_page = 50
    readonly_fields = ['fileLink']
    fieldsets = [
        ("Request Information", {'fields': ['resource', 'profile', 'fileLink', 'status', 'reason']})
    ]
    actions = ['approve_status']

    def save_model(self, request, obj, form, change):
        # see notes on http://nyphp.org/phundamentals/8_Preventing-Email-Header-Injection
        # send email depending on the status of data request

        site_admin_email = settings.THEME_ACCOUNT_CONTACT_EMAIL
        context = {
            'site_admin_email': site_admin_email,
        }

        # data is available via POST method
        status = unicode(request.POST.get('status', 'PENDING')).encode('utf8')
        if status == 'APPROVED':
            # @todo check ADMIN_PERMISSIONS and LAYER_ADMIN_PERMISSIONS variables
            resource_id = request.POST.get('resource')
            requested_resource = Imagery.objects.get(pk=int(resource_id))
            requested_link = settings.SITEURL + 'uas/imagery/' + unicode(resource_id).encode('utf8')

            context['requested_resource'] = requested_resource
            context['requested_link'] = requested_link

            obj.date_approved = timezone.now()

            subject = 'Notification of Approval'

            html_content = render_to_string('parmap_data_request/email_approval_uas.html', context)

        elif status == 'REJECTED':
            subject = 'Denial of Request'

            resource_id = request.POST.get('resource')
            requested_resource = Imagery.objects.get(pk=resource_id)

            #@TODO  get reasons from POST data
            reasons = request.POST.getlist('reason')

            reasons_arr = []
            reasons_messages = []
            for post_reason in reasons:
                req_reason = RequestReason.objects.get(pk=post_reason)
                reasons_messages.append(unicode(req_reason.message).encode('utf8'))
                reasons_arr.append(req_reason)

            obj.reason = reasons_arr
            context['requested_resource'] = requested_resource
            context['reasons'] = reasons_messages
            html_content = render_to_string('parmap_data_request/email_rejection.html', context)

            # @todo if permission to download resource should be valid for 2-3 weeks only, cron job should do the cleanup
            # make the expiry configurable in settings.py
        elif status == 'PENDING':
            subject = 'Request for further details'
            #@TODO  get reasons from POST data
            reasons = request.POST.getlist('reason')

            reasons_arr = []
            reasons_messages = []
            for post_reason in reasons:
                req_reason = RequestReason.objects.get(pk=post_reason)
                reasons_messages.append(unicode(req_reason.message).encode('utf8'))
                reasons_arr.append(req_reason)

            obj.reason = reasons_arr
            context['reasons'] = reasons_messages
            html_content = render_to_string('parmap_data_request/email_further_details.html', context)
        else:
            # status is AWAITING, do nothing
            pass

        if (status != 'AWAITING') and (status != ''):
            # this strips the html, so people will have the text as well.
            text_content = strip_tags(html_content)

            sender = settings.DEFAULT_FROM_EMAIL

            recipient = unicode(obj.profile.email).encode('utf8')
            recipients = [recipient]

            try:
                # create the email, and attach the HTML version as well.
                message = EmailMultiAlternatives(subject, text_content, sender, recipients)
                message.attach_alternative(html_content, "text/html")
                message.send()

            except Exception as e:
                # @todo, put this on a error log handler
                 print('There was an error sending an email: ', e)

        obj.save()

admin.site.register(Imagery, ImageryAdmin)
admin.site.register(UASRequest, UASRequestAdmin)
