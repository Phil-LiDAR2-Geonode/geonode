from django.db import models

class Filter(models.Model):
    filter = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    def __unicode__(self):
        return self.filter