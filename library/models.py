from django.db import models
from django.contrib.auth.models import User


class MediaItem(models.Model):
    TMDB_MEDIA_TYPES = [
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
    ]

    tmdb_id = models.PositiveIntegerField()
    media_type = models.CharField(max_length=10, choices=TMDB_MEDIA_TYPES)

    class Meta:
        unique_together = ('tmdb_id', 'media_type')
        ordering = ['media_type', 'tmdb_id']

    def __str__(self):
        return f"{self.media_type.capitalize()} #{self.tmdb_id}"


class UserItem(models.Model):
    STATUS_WATCHED = 'watched'
    STATUS_PLANNED = 'planned'
    STATUS_FAVORITE = 'favorite'

    STATUS_CHOICES = [
        (STATUS_WATCHED, 'Watched'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_FAVORITE, 'Favorite'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'media_item', 'status')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.media_item} ({self.status})"
