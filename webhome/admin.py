from django.contrib import admin

from webhome.models import Article, Category, ContactMessage, NosServices


# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'published')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'message', 'created_at')
    list_filter = ('name', 'email', 'created_at')


@admin.register(NosServices)
class NosServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','category' )
    list_filter = ('name', 'name', 'category')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    list_filter = ('name', 'name',)
