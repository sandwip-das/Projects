from django.contrib import admin
from .models import Profile, Category, Tag, Post, Comment, PostInteraction, HomeContent, ImportantLink
# from django_summernote.admin import SummernoteModelAdmin

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'views_count')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class HomeContentAdmin(admin.ModelAdmin):
    # Hide deprecated fields
    exclude = ('short_description', 'motto')
    list_display = ('__str__', 'marquee_text')

admin.site.register(Profile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(PostInteraction)
admin.site.register(HomeContent, HomeContentAdmin)
admin.site.register(ImportantLink)
