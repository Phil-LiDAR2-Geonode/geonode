import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import string

from geonode.base.models import ResourceBase
from geonode.people.models import Profile

# Create your models here.
class RequestReason(models.Model):
    message = models.CharField(max_length=250)
    date_created = models.DateTimeField('date created', default=timezone.now)
    date_updated = models.DateTimeField('date updated', default=timezone.now)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.message

class DataRequest(models.Model):
    class Meta:
        verbose_name = "Request Information"

    STATUS_CHOICES = (
        ('AWAITING', ''),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    # models.UUIDField crashes on django 1.6.x
    request_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False)

    resource = models.ForeignKey(ResourceBase)
    profile = models.ForeignKey(Profile)

    letter_filename = models.FileField(upload_to="data_request/")

    status = models.CharField(
        blank=True,
        max_length=10,
        choices=STATUS_CHOICES,
        default='AWAITING'
    )

    reason = models.ManyToManyField(RequestReason, blank=True)

    date_created = models.DateTimeField('date created', default=timezone.now)
    date_updated = models.DateTimeField('date updated', default=timezone.now)
    date_approved = models.CharField('date approved', max_length=50, blank=True)

    def fileLink(self):
        if self.letter_filename:
            media_url = os.path.join(settings.PROJECT_ROOT, string.lstrip(settings.MEDIA_URL, '/'))
            media_url = string.replace(unicode(self.letter_filename.url).encode('utf8'), media_url, '')
            media_url = settings.MEDIA_URL + media_url
            media_name = os.path.basename(unicode(self.letter_filename.name).encode('utf8'))

            return '<a href="' + media_url + '">' + media_name + '</a>'
        else:
            return '<a href="''"></a>'
    fileLink.allow_tags = True
    fileLink.short_description = "Request Letter"

#    def __unicode__(self):  # Python 3: def __str__(self):
        # we need to provide string value on object representation
#        return self.request_id.urn[9:]
