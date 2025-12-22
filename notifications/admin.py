from django.contrib import admin
from announcements.models import ReadReceipt

@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ("announcement", "user", "read_at")
    list_filter = ("announcement", "user")

