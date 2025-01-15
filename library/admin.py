from django.contrib import admin
from .models import Genre, Item, UserItem


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'release_date', 'created_at')
    list_filter = ('item_type', 'genres')
    search_fields = ('title',)


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'watched', 'progress', 'added_at')
    list_filter = ('watched', 'added_at')
    search_fields = ('user__username', 'item__title')
