from django.db import models
from django.contrib.auth.models import User


class ItemType(models.TextChoices):
    MOVIE = 'MV', 'Movie'
    TV_SERIES = 'TVS', 'TV Series'
    ANIME = 'AN', 'Anime'


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=3, choices=ItemType.choices, default=ItemType.MOVIE)
    genres = models.ManyToManyField(Genre, related_name='items')
    release_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class UserItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_users')
    watched = models.BooleanField(default=False)
    progress = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.item.title}"
