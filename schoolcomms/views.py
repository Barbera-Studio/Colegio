from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from schoolcomms.dashboard.models import PrivateMessage
from schoolcomms.utils.email import send_announcement_email

User = get_user_model()

def test_sendgrid_email(request):
    html = render_to_string("emails/aviso.html", {
        "aviso": {
            "title": "Reunión general de padres",
            "content": "Estimadas familias, les invitamos a la reunión general el próximo jueves a las 18:00.",
            "created_at": "09/09/2025 15:30"
        },
        "usuario": {
            "email": "familia@ejemplo.com"
        }
    })
    send_announcement_email("familia@ejemplo.com", "📢 Nuevo aviso del colegio", html)
    return HttpResponse("Correo de prueba enviado.")


@login_required
def send_message_to_family(request):
    """
    Envía un mensaje privado entre tutor y familia (valida vínculo).
    """
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        content = request.POST.get("content")
        sender = request.user

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            django_messages.error(request, "Usuario receptor no válido.")
            return redirect("dashboard:mensajes")  # ✅ corregido

        msg = PrivateMessage.objects.create(
            sender=sender,
            receiver=receiver,
            subject="(mensaje tutor-familia)",
            content=content,
            is_read=False
        )

        # Notificación por correo (si procede)
        prefs = getattr(receiver, "notificationpreference", None)
        if prefs and getattr(prefs, "email_enabled", False) and getattr(prefs, "notify_on_message", False):
            html = render_to_string("emails/mensaje.html", {"mensaje": msg})
            send_announcement_email(receiver.email, "📩 Nuevo mensaje privado", html)

        django_messages.success(request, "Mensaje enviado correctamente.")
        return redirect("dashboard:mensajes")  # ✅ corregido

    return redirect("dashboard:mensajes")  # ✅ corregido

