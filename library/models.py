from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    ITEM_TYPES = [
        ('TV', 'TV Series'),
        ('AN', 'Anime'),
        ('MV', 'Movie'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=2, choices=ITEM_TYPES)
    genres = models.ManyToManyField(Genre, related_name='items')
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class UserItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f"{self.user.username} - {self.item.title}"
