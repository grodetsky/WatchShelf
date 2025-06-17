from django.contrib import admin
from .models import MediaItem, UserItem, Collection


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


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'media_count', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username')
    raw_id_fields = ('user',)
    filter_horizontal = ('media_items',)
    ordering = ('-updated_at',)

    def media_count(self, obj):
        return obj.media_items.count()

    media_count.short_description = 'Media Items'
