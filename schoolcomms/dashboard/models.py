from datetime import time

from django.conf import settings
from django.db import models
from django.utils import timezone


# ---------------------- TAREAS ----------------------
class Tarea(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    fecha_entrega = models.DateField()
    hora = models.TimeField(default=time(8, 0))
    completada = models.BooleanField(default=False)
    fecha_completado = models.DateField(null=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["fecha_entrega", "hora"]
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def save(self, *args, **kwargs):
        if self.completada and not self.fecha_completado:
            self.fecha_completado = timezone.now().date()
        elif not self.completada:
            self.fecha_completado = None
        super().save(*args, **kwargs)

    def estado(self):
        return "✅ Completada" if self.completada else "⏳ Pendiente"

    def __str__(self):
        return f"Tarea: {self.titulo} ({self.fecha_entrega.strftime('%d/%m/%Y')})"


# ---------------------- INCIDENCIAS ----------------------
class Incidencia(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("revision", "En revisión"),
        ("resuelta", "Resuelta"),
    ]

    CATEGORIAS = [
        ("tecnica", "Técnica"),
        ("disciplinaria", "Disciplinaria"),
        ("otro", "Otro"),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default="otro")
    estado = models.CharField(max_length=50, choices=ESTADOS, default="pendiente")
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.titulo} ({self.estado})"


# ---------------------- AVISOS ----------------------
class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avisos_creados'
    )
    destinatarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='avisos_recibidos'
    )

    def __str__(self):
        return f"Aviso: {self.titulo}"


# ---------------------- MENSAJES PRIVADOS ----------------------
class PrivateMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.sender} a {self.receiver}: {self.subject}"


# ---------------------- NOTIFICACIONES ----------------------
class Notification(models.Model):
    TIPOS = [
        ("info", "Información"),
        ("warning", "Advertencia"),
        ("error", "Error"),
        ("success", "Éxito"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS, default="info")
    titulo = models.CharField(max_length=200, default="Notificación")
    contenido = models.TextField(default="")
    url = models.URLField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    mensaje = models.ForeignKey("PrivateMessage", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"[{self.tipo}] {self.titulo} → {self.user}"




# ---------------------- ANUNCIOS ----------------------
class Announcement(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name="dashboard_announcement_reads"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_announcement_reads_by_user"
    )
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} leyó {self.announcement}"


class NotificationPreference(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_notification_preferences"
    )
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferencias de {self.user}"


# ---------------------- ASISTENCIA ----------------------
class Asistencia(models.Model):
    alumno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(
        max_length=10,
        choices=[('presente', 'Presente'), ('ausente', 'Ausente')],
        default='presente'
    )

    def __str__(self):
        return f"{self.alumno} - {self.fecha} ({self.estado})"
