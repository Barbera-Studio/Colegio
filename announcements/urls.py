from django.urls import path
from . import views
from .views import export_announcements_pdf

app_name = "announcements"

urlpatterns = [
    path("dashboard/", views.announcement_list, name="dashboard"),
    path("export/pdf/", export_announcements_pdf, name="export_pdf"),
]
