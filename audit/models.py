from django.db import models
from core.models import CustomUser

class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)

class Consent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(auto_now_add=True)
    document_version = models.CharField(max_length=20)
