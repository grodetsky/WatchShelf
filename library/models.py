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
    STATUS_PLANNED = 'planned'
    STATUS_WATCHING = 'watching'
    STATUS_REWATCHING = 'rewatching'
    STATUS_ON_HOLD = 'on_hold'
    STATUS_DROPPED = 'dropped'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PLANNED, 'Plan to Watch'),
        (STATUS_WATCHING, 'Watching'),
        (STATUS_REWATCHING, 'Rewatching'),
        (STATUS_ON_HOLD, 'On Hold'),
        (STATUS_DROPPED, 'Dropped'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'media_item')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.media_item} ({self.status})"


class Collection(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media_items = models.ManyToManyField(MediaItem, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"
