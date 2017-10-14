from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    image = models.FileField(upload_to="article_img/")
    def __unicode__(self):
        return self.title
