# dashboard/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Aviso, PrivateMessage, Tarea, Notification
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in

@receiver(post_save, sender=Aviso)
def aviso_notif(sender, instance, created, **kwargs):
    if created:
        for user in instance.destinatarios.all():
            Notification.objects.create(
                user=user,
                tipo="aviso",
                titulo="Nuevo aviso",
                contenido=instance.titulo,
                url=f"/dashboard/avisos/{instance.id}/"
            )

@receiver(post_save, sender=PrivateMessage)
def mensaje_notif(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            tipo="mensaje",
            titulo=f"Nuevo mensaje de {instance.sender}",
            contenido=instance.content[:50] + "...",
            url=f"/dashboard/mensajes/{instance.id}/"
        )

@receiver(user_logged_in)
def registrar_asistencia_automatica(sender, request, user, **kwargs):
    from .models import Asistencia  # Import dentro de la función
    hoy = timezone.now().date()
    Asistencia.objects.get_or_create(
        alumno=user,
        fecha=hoy,
        defaults={"estado": "presente"}
    )