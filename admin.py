from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Video, UserProfile, Comment


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'duration_display', 'views', 'likes_count', 'uploaded_at']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['title', 'description', 'uploaded_by__username']
    list_select_related = ['uploaded_by']
    date_hierarchy = 'uploaded_at'
    readonly_fields = ['views', 'uploaded_at', 'thumbnail_preview']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'file', 'thumbnail', 'thumbnail_preview')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at', 'views', 'likes'),
        }),
    )

    actions = ['delete_inappropriate']

    def duration_display(self, obj):
        return f'{obj.views} views'
    duration_display.short_description = 'Popularity'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.thumbnail.url)
        return '-'
    thumbnail_preview.short_description = 'Thumbnail Preview'

    @admin.action(description='Delete selected videos (inappropriate content)')
    def delete_inappropriate(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} video(s) deleted for inappropriate content.')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Comment'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture', 'avatar_preview']
    search_fields = ['user__username', 'user__email']

    def avatar_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 50%;" />', obj.profile_picture.url)
        return '-'
    avatar_preview.short_description = 'Avatar'
