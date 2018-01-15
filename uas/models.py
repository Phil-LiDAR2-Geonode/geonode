import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import string

from parmap_data_request.models import RequestReason
from geonode.people.models import Profile

class Imagery(models.Model):
    title = models.CharField(max_length=200)
    date_acquired = models.DateField("Date")
    location = models.CharField(max_length=200)
    sensor = models.CharField(max_length=20)
    resolution = models.IntegerField()
    file_size = models.CharField(max_length=20)

    zipped_file = models.FileField(upload_to="uas_imagery")
    thumb_file = models.FileField(upload_to='uas_thumbnail')

    def __unicode__(self):
        return self.title

class UASRequest(models.Model):
    class Meta:
        verbose_name = "UAS Request"

    STATUS_CHOICES = (
        ('AWAITING', ''),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    resource = models.ForeignKey(Imagery)
    profile = models.ForeignKey(Profile)

    letter_filename = models.FileField(upload_to="uas_request/")

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
