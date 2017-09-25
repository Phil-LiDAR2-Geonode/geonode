from django.contrib import admin
#from django.core.mail import send_mail
#from smtplib import SMTPException # python class

from .models import DataRequest, RequestReason

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.shortcuts import get_object_or_404
from geonode.base.models import ResourceBase
from geonode.people.models import Profile
from geonode.layers.models import Layer
from django.utils import timezone
from guardian.shortcuts import assign_perm

from parmap_data_request.forms import DataRequestForm

from django.contrib.staticfiles.storage import staticfiles_storage
import csv

class RequestReasonAdmin(admin.ModelAdmin):
    list_display = ('message', 'date_created', 'date_updated')
    list_per_page = 50
    fieldsets = [
        ("Reason for approval/pending action", {'fields': ['message']})
    ]

class DataRequestAdmin(admin.ModelAdmin):
    form = DataRequestForm
    list_display = ('resource', 'profile', 'date_created', 'status')
    list_per_page = 50
    readonly_fields = ['fileLink']
    fieldsets = [
        ("Request Information", {'fields': ['resource', 'profile', 'fileLink', 'status', 'reason']})
    ]
    actions = ['approve_status']

    def approve_status(self, request, queryset):
        approved_count = 0
        ignored_count = 0

        subject = 'Notification of Approval'
        site_admin_email = settings.THEME_ACCOUNT_CONTACT_EMAIL
        context = {'site_admin_email': site_admin_email,}

        # since this is bulk approval, parse the csv contents only once
        csv_contents = []
        muncode_file = staticfiles_storage.path('geonode/files/NSO_Muni.csv')
        with open(muncode_file, 'rb') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                csv_contents.append(row[3])

        for data_request in queryset:
            if data_request.status == 'APPROVED':
                ignored_count = ignored_count + 1
            else:
                requesting_user = data_request.profile
                requested_resource = data_request.resource
                resource_type = unicode(requested_resource.polymorphic_ctype.model).encode('utf8')
                if resource_type == "layer":
                    resources = []
                    layer_title = unicode(requested_resource.title).encode('utf8')
                    layer_resource = get_object_or_404(Layer, title=layer_title)
                    resource_keywords = layer_resource.keywords.names()

                    for keyword in resource_keywords:
                        if keyword in csv_contents:
                            for related_layer in Layer.objects.filter(keywords__name__in=[keyword]):
                                resources.append(related_layer)

                    # remove duplicate items
                    resources = set(resources)
                    # convert back to indexable object
                    resources = list(resources)

                    resource_links = []
                    for related_layer in resources:
                        resource_link = (
                            unicode(related_layer.title).encode('utf8'),
                            settings.SITEURL + 'layers/geonode:' + unicode(related_layer.name).encode('utf8')
                        )
                        resource_links.append(resource_link)

                        layer_resourcebase = related_layer.get_self_resource()
                        try:
                            assign_perm('download_resourcebase', requesting_user, layer_resourcebase)
                        except Exception as e:
                            print('There was an error assigning permission to %s for %s' % (layer_resourcebase, requesting_user))
                else:
                    resource_link = (
                        requested_resource.title,
                        settings.SITEURL + 'documents/' + unicode(requested_resource.id).encode('utf8')
                    )
                    resource_links = [resource_link]
                    assign_perm('download_resourcebase', requesting_user, requested_resource)

                context['resource_links'] = resource_links
                data_request.date_approved = timezone.now()
                data_request.status = 'APPROVED'
                data_request.save()
                approved_count = approved_count + 1

                html_content = render_to_string('parmap_data_request/email_approval.html', context)
                text_content = strip_tags(html_content)
                sender = settings.DEFAULT_FROM_EMAIL
                recipient = unicode(data_request.profile.email).encode('utf8')
                recipients = [recipient]

                try:
                    # create the email, and attach the HTML version as well.
                    message = EmailMultiAlternatives(subject, text_content, sender, recipients)
                    message.attach_alternative(html_content, "text/html")
                    message.send()

                except Exception as e:
                    # @todo, put this on a error log handler
                     print('There was an error sending an email: ', e)


        if approved_count == 1:
            message_bit = "One request was successfully approved, %s request(s) were already approved" % ignored_count
        else:
            message_bit = "%s requests were successfully approved, %s request(s) were already approved" % (approved_count, ignored_count)
        self.message_user(request, message_bit)

    approve_status.short_description = "Approve selected request"

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
            requested_resource = get_object_or_404(ResourceBase, id=resource_id)
            requesting_user = obj.profile

            resource_type = unicode(requested_resource.polymorphic_ctype.model).encode('utf8')
            resources = []
            if resource_type == "layer":
                layer_title = unicode(requested_resource.title).encode('utf8')
                layer_resource = get_object_or_404(Layer, title=layer_title)
                resource_keywords = layer_resource.keywords.names()
                csv_contents = []

                muncode_file = staticfiles_storage.path('geonode/files/NSO_Muni.csv')
                with open(muncode_file, 'rb') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    for row in csv_reader:
                        csv_contents.append(row[3])

                for keyword in resource_keywords:
                    if keyword in csv_contents:
                        for related_layer in Layer.objects.filter(keywords__name__in=[keyword]):
                            resources.append(related_layer)

                # remove duplicate items
                resources = set(resources)
                # convert back to indexable object
                resources = list(resources)

                resource_links = []
                for related_layer in resources:
                    resource_link = (
                        unicode(related_layer.title).encode('utf8'),
                        settings.SITEURL + 'layers/geonode:' + unicode(related_layer.name).encode('utf8')
                    )
                    resource_links.append(resource_link)
                    layer_resourcebase = related_layer.get_self_resource()
                    try:
                        assign_perm('download_resourcebase', requesting_user, layer_resourcebase)
                    except Exception as e:
                        print('There was an error assigning permission to %s for %s' % (layer_resourcebase, requesting_user))
            else:

                resource_link = (
                    requested_resource.title,
                    settings.SITEURL + 'documents/' + unicode(requested_resource.id).encode('utf8')
                )
                resource_links = [resource_link]
                assign_perm('download_resourcebase', requesting_user, requested_resource)

            context['resource_links'] = resource_links
            obj.date_approved = timezone.now()
            subject = 'Notification of Approval'
            html_content = render_to_string('parmap_data_request/email_approval.html', context)

        elif status == 'REJECTED':
            subject = 'Denial of Request'

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

admin.site.register(RequestReason, RequestReasonAdmin)
admin.site.register(DataRequest, DataRequestAdmin)
