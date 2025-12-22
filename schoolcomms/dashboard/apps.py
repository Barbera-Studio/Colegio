from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

class DashboardConfig(AppConfig):
    name = 'schoolcomms.dashboard'

    def ready(self):
        import schoolcomms.dashboard.signals