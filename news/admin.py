from news.models import Article, Headline
from django.contrib import admin

myModels = [Article, Headline]
admin.site.register(myModels)
