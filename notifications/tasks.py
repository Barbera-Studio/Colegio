from celery import shared_task
from django.utils import timezone
from announcements.models import Announcement
from django.core.mail import send_mail

@shared_task
def send_daily_summary():
    today = timezone.now().date()
    announcements = Announcement.objects.filter(created_at__date=today)

    grouped = {}
    for a in announcements:
        for group in a.groups.all():
            grouped.setdefault(group, []).append(a)

    for group, avisos in grouped.items():
        emails = [tutor.email for tutor in group.tutors.all()]
        content = "\n\n".join([f"{a.title}\n{a.content}" for a in avisos])
        send_mail(
            subject="Resumen diario de avisos",
            message=content,
            from_email="[email protected]",
            recipient_list=emails,
        )

@shared_task(bind=True)
def tarea_que_falla(self):
    raise Exception("Simulación de error")
