from news.models import Article, Headline
from django.contrib import admin

class HeadlineAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'creation_date')
    list_per_page = 50

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'creation_date')
    list_per_page = 50

admin.site.register(Headline, HeadlineAdmin)
admin.site.register(Article, ArticleAdmin)
