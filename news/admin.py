from news.models import Article
from django.contrib import admin

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'start_date', 'end_date', 'is_headline', 'creation_date')
    list_per_page = 50

admin.site.register(Article, ArticleAdmin)
