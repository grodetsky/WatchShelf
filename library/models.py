from django.db import models
from django.contrib.auth.models import User


class MediaItem(models.Model):
    MEDIA_TYPES = [
        ('TV', 'TV Series'),
        ('ANIME', 'Anime'),
        ('MOVIE', 'Movie'),
    ]

    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    description = models.TextField(blank=True, null=True)
    release_year = models.IntegerField()

    def __str__(self):
        return self.title


class UserItem(models.Model):
    STATUS_CHOICES = [
        ('WATCHED', 'Watched'),
        ('WATCHING', 'Watching'),
        ('PLAN_TO_WATCH', 'Plan to Watch'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.media_item.title} ({self.status})"
