# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    is_premium = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    hls_folder = models.CharField(max_length=255)  # e.g., 'hls/movie1/index.m3u8'
    price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)


class PremiumRequest(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)


class StreamToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at


class WatchLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class BlockedUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    reason = models.TextField()
    blocked_at = models.DateTimeField(auto_now_add=True)


class VideoUpload(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class AdminActionLog(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="admin_actions")
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
