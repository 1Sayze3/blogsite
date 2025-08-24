from django.contrib import admin
from .models import Post, Comment, Profile, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "view_count")
    search_fields = ("title", "content")
    list_filter = ("created_at",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PostImageInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")