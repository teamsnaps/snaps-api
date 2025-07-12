from django.contrib import admin

# Register your models here.
from snapsapi.apps.posts.models import Post, Tag, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption_preview', 'likes_count', 'comments_count', 'created_at', 'is_active', 'is_deleted')
    list_filter = ('is_active', 'is_deleted', 'is_public', 'created_at')
    search_fields = ('caption', 'user__username')
    inlines = [PostImageInline]

    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'created_at')
    list_filter = ('is_featured',)
    search_fields = ('name',)


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
