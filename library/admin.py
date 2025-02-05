from django.contrib import admin
from .models import MediaItem, UserItem


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'release_year')
    list_filter = ('media_type',)
    search_fields = ('title',)


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_item', 'status', 'updated_on')
    list_filter = ('status',)
    search_fields = ('user__username', 'media_item__title')
