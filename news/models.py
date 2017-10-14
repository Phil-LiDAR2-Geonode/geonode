from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    image1 = models.FileField('image 1', upload_to="article_img/")
    image2 = models.FileField('image 2', upload_to="article_img/")
    def __unicode__(self):
        return self.title

class Headline(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    image1 = models.FileField('image 1', upload_to="article_img/")
    image2 = models.FileField('image 2', upload_to="article_img/")
    def __unicode__(self):
        return self.title
