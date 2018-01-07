from django.db import models
from datetime import datetime

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image1 = models.FileField("image 1", upload_to="article_img/", blank=True)
    image2 = models.FileField("image 2", upload_to="article_img/", blank=True)
    is_headline = models.BooleanField("Set as headline")
    creation_date = models.DateTimeField(auto_now=True, editable=False)
    def __unicode__(self):
        return self.title
