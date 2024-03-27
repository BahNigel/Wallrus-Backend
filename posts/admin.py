from django.contrib import admin

from posts.models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'slug', 'category')

admin.site.register(Post, PostAdmin)
