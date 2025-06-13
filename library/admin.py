from django.contrib import admin
from .models import MediaItem, UserItem


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('tmdb_id', 'media_type')
    list_filter = ('media_type',)
    search_fields = ('tmdb_id',)


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_item', 'status', 'added_at', 'updated_at')
    list_filter = ('status', 'media_item__media_type', 'user')
    search_fields = (
        'user__username',
        'media_item__tmdb_id',
    )
    raw_id_fields = ('user', 'media_item')
    ordering = ('-updated_at',)
