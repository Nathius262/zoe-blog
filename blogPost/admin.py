import mptt
from django.contrib import admin
from . import models
from blogPost.models import Category, Like
from mptt.admin import MPTTModelAdmin


@admin.register(models.BlogPost)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_published', 'date_updated')
    search_fields = ('title', 'body')


admin.site.register(Category)
admin.site.register(models.Comment, MPTTModelAdmin)
admin.site.register(Like)
