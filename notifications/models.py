from django.db import models
from core.models import CustomUser

class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    PUSH = "push", "Push Web"

class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)

class UserNotificationPreference(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    daily_digest = models.BooleanField(default=True)

class NotificationLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    reference = models.CharField(max_length=255, blank=True)

