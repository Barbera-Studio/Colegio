from django.db import models
from core.models import Group, CustomUser


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AnnouncementRead(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="announcement_reads")
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'announcement')

    def __str__(self):
        return f"{self.user} leyó {self.announcement}"


class ReadReceipt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="announcement_receipts")
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("announcement", "user")

    def __str__(self):
        return f"Recibo de {self.user} para {self.announcement}"


class ClassGroup(models.Model):
    name = models.CharField(max_length=80)  # "2º ESO A"
    stage = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name
