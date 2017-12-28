from django.db import models

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
