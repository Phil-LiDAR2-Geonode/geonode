from django.db import models
from geonode.people.models import Profile

class DataDownload(models.Model):
    class Meta:
        verbose_name = "Data Download"
    username = models.ForeignKey(Profile)
    email = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    data_id = models.IntegerField()
    data_downloaded = models.CharField(max_length=200)
    data_type = models.CharField(max_length=100)
    date_downloaded = models.DateTimeField()
