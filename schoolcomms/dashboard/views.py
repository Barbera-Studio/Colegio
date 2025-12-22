# views.py (unificado, limpio y completo)
from datetime import datetime, date, timedelta
import random
import json
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.functions import ExtractWeekDay
from django.db.models import Count
from .models import Notification, PrivateMessage

# Importa aquí los modelos y formularios que usas en tu proyecto.
# Ajusta los imports si los nombres/paths son distintos en tu repo.
from schoolcomms.dashboard.models import (
    Aviso, Tarea, Incidencia,
    Announcement, AnnouncementRead,
    PrivateMessage, Notification, Asistencia
)
from schoolcomms.dashboard.forms import TareaForm, IncidenciaForm, AvisoForm
from .forms import PrivateMessageForm, EstadoIncidenciaForm
from core.models import CustomUser  # si tu app se llama distinto, ajústalo

User = get_user_model()

# ---------------------- CONFIGURACIÓN ESCOLAR / CONSTANTES ----------------------

INICIO_CURSO = date(2025, 9, 8)
FIN_CURSO = date(2026, 6, 19)

FESTIVOS = {
    date(2025, 10, 9),
    date(2025, 10, 12),
    date(2025, 11, 1),
    date(2025, 12, 6),
    date(2025, 12, 8),
    date(2026, 3, 19),
    date(2026, 5, 1),
}

VACACIONES = set()
VACACIONES.update([date(2025, 12, d) for d in range(20, 32)])  # Navidad
VACACIONES.update([date(2026, 1, d) for d in range(1, 8)])
VACACIONES.update([date(2026, 3, d) for d in range(28, 32)])  # Semana Santa
VACACIONES.update([date(2026, 4, d) for d in range(1, 6)])

# ---------------------- UTILIDADES ----------------------


def es_dia_lectivo(fecha: date):
    """
    Devuelve (bool, motivo_str). Reusa constantes INICIO_CURSO, FIN_CURSO, FESTIVOS, VACACIONES.
    """
    if fecha < INICIO_CURSO or fecha > FIN_CURSO:
        return False, "Fuera del calendario escolar"
    if fecha.weekday() >= 5:
        return False, "Fin de semana"
    if fecha in FESTIVOS:
        return False, "Festivo oficial"
    if fecha in VACACIONES:
        return False, "Vacaciones escolares"
    return True, "Día lectivo"


def generar_asistencia_curso(hasta_fecha):
    historial = []
    fecha = INICIO_CURSO
    while fecha <= hasta_fecha:
        es_lectivo, _ = es_dia_lectivo(fecha)
        if es_lectivo:
            # Simulación: alternancia de asistencia
            presente = 1 if fecha.day % 3 != 0 else 0
            ausente = 1 - presente
            historial.append({
                "fecha": fecha,
                "presente": presente,
                "ausente": ausente
            })
        fecha += timedelta(days=1)

    totales = {
        "dias_lectivos": len(historial),
        "presentes": sum(d["presente"] for d in historial),
        "ausentes": sum(d["ausente"] for d in historial)
    }

    return {
        "historial": historial,
        "totales": totales
    }



def obtener_ultimos_dias_lectivos(n=7, hasta_fecha: date = None):
    """
    Devuelve una lista de las últimas 'n' fechas lectivas (incluye el más reciente anterior a 'hasta_fecha').
    Por defecto 'n' = 7.
    """
    if hasta_fecha is None:
        hasta_fecha = date.today()
    dias_lectivos = []
    i = 0
    # empezamos en el mismo día y vamos hacia atrás hasta tener n lectivos
    while len(dias_lectivos) < n:
        dia = hasta_fecha - timedelta(days=i)
        if es_dia_lectivo(dia)[0]:
            dias_lectivos.append(dia)
        i += 1
        # seguridad para no entrar en bucles infinitos (p. ej. si INICIO_CURSO logic)
        if i > 365 * 5:
            break
    dias_lectivos.reverse()  # orden cronológico ascendente
    return dias_lectivos


def calcular_nota_semanal(base, nombre):
    semana = datetime.now().isocalendar()[1]
    semilla = sum(ord(c) for c in nombre) + semana
    variacion = (semilla % 5) - 2  # -2 a +2
    nueva = max(50, min(100, base + variacion))
    return nueva


# ---------------------- VISTAS: DASHBOARD ----------------------


@login_required
def dashboard_home(request):
    user = request.user

    # === Querysets base ===
    tareas_qs = Tarea.objects.filter(autor=user)
    avisos_qs = Aviso.objects.filter(autor=user)
    incidencias_qs = Incidencia.objects.filter(autor=user)

    # Mensajes: separa todos vs no leídos (para UI y métricas)
    mensajes_all_qs = PrivateMessage.objects.filter(receiver=user)
    mensajes_unread_qs = mensajes_all_qs.filter(is_read=False)

    notificaciones = Notification.objects.filter(user=user, leida=False).order_by('-creado')[:20]

    # === Datos básicos (sliced y ordenados) ===
    tareas = tareas_qs.order_by('-fecha_entrega')[:5]
    avisos = avisos_qs.order_by('-fecha_publicacion')[:5]
    # El card de mensajes muestra SOLO no leídos
    mensajes = mensajes_unread_qs.order_by('-created_at')[:5]
    incidencias = incidencias_qs.order_by('-fecha_reporte')[:5]

    # === Estadísticas resumidas ===
    total_tareas = tareas_qs.count()
    completadas = tareas_qs.filter(completada=True).count()
    progreso_academico = int((completadas / total_tareas) * 100) if total_tareas > 0 else 0

    # Asistencia para hoy
    hoy = date.today()
    asistencia_data = generar_asistencia_curso(hasta_fecha=hoy)
    asistencia_historial_curso = asistencia_data["historial"]
    totales_asistencia = asistencia_data["totales"]

    total_presentes = sum(d["presente"] for d in asistencia_historial_curso)
    total_ausentes = sum(d["ausente"] for d in asistencia_historial_curso)

    # Rendimiento por materias (simulado)
    materias_base = [
        {"nombre": "Matemáticas", "nota": 85},
        {"nombre": "Lengua", "nota": 78},
        {"nombre": "Historia", "nota": 92},
        {"nombre": "Física", "nota": 74},
        {"nombre": "Química", "nota": 88},
        {"nombre": "Biología", "nota": 81},
        {"nombre": "Geografía", "nota": 69},
        {"nombre": "Educación Física", "nota": 95},
        {"nombre": "Inglés", "nota": 79},
        {"nombre": "Economía", "nota": 68},
    ]
    rendimiento_materias = [
        {"nombre": m["nombre"], "nota": calcular_nota_semanal(m["nota"], m["nombre"])}
        for m in materias_base
    ]

    eventos_proximos = []  # placeholder

    # === Cards dinámicos ===
    def items_from_queryset(qs, label_attr="titulo", fallback="Sin elementos", max_items=5, fmt=None):
        items = []
        for o in qs[:max_items]:
            items.append(fmt(o) if fmt else getattr(o, label_attr, str(o)))
        return items if items else [fallback]

    cards = [
        {
            "title": "Avisos",
            "icon": "fa-bullhorn",
            "color": "from-blue-500 to-blue-700",
            "items": items_from_queryset(avisos, label_attr="titulo", fallback="Sin avisos", max_items=5, fmt=lambda o: f"{o.titulo}")
        },
        {
            "title": "Mensajes",
            "icon": "fa-envelope",
            "color": "from-green-500 to-green-700",
            # Importante: items desde NO LEÍDOS
            "items": items_from_queryset(
                mensajes,
                label_attr="subject",
                fallback="Sin mensajes",
                max_items=5,
                fmt=lambda m: f"{getattr(m.sender, 'username', 'Desconocido')}: {m.subject}"
            )
        },
        {
            "title": "Tareas",
            "icon": "fa-tasks",
            "color": "from-purple-500 to-purple-700",
            "items": items_from_queryset(
                tareas,
                label_attr="titulo",
                fallback="Sin tareas",
                max_items=5,
                fmt=lambda t: f"{t.titulo} - {'✅' if t.completada else '❌'}"
            )
        },
        {
            "title": "Incidencias",
            "icon": "fa-triangle-exclamation",
            "color": "from-red-500 to-red-700",
            "items": items_from_queryset(
                incidencias,
                label_attr="descripcion",
                fallback="Sin incidencias",
                max_items=5,
                fmt=lambda i: (i.titulo if hasattr(i, 'titulo') else (i.descripcion[:60] + ("..." if len(i.descripcion) > 60 else "")))
            )
        },
    ]

    # === Actividad global (puedes contar todos, no solo no leídos) ===
    activity_labels = ["Avisos", "Mensajes", "Tareas", "Incidencias"]
    activity_values = [
        avisos_qs.count(),
        mensajes_all_qs.count(),  # total de mensajes, no solo no leídos
        tareas_qs.count(),
        incidencias_qs.count()
    ]

    # === Actividad reciente: tareas completadas últimos 7 días lectivos ===
    dias_lectivos = obtener_ultimos_dias_lectivos(7, hasta_fecha=hoy)
    dias_semana_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    labels_ultimos = [f"{dias_semana_es[d.weekday()]} {d.strftime('%d/%m')}" for d in dias_lectivos]
    values_ultimos = [tareas_qs.filter(completada=True, fecha_completado=d).count() for d in dias_lectivos]
    if sum(values_ultimos) == 0:
        values_ultimos = [random.randint(0, 5) for _ in labels_ultimos]

    # === Conteo de días lectivos desde inicio del curso ===
    dias_desde_inicio = (hoy - INICIO_CURSO).days
    dias_lectivos_contados = sum(
        1 for i in range((hoy - INICIO_CURSO).days + 1)
        if es_dia_lectivo(INICIO_CURSO + timedelta(days=i))[0]
    )

    # === Contexto final (incluye unread_count para el badge del card) ===
    context = {
        "avisos": avisos,
        "mensajes": mensajes,  # SOLO no leídos para el card
        "unread_count": mensajes_unread_qs.count(),
        "tareas": tareas,
        "incidencias": incidencias,
        "notificaciones": notificaciones,
        "cards": cards,
        "progreso_academico": progreso_academico,
        "asistencia_historial_curso": asistencia_historial_curso,
        "rendimiento_materias": rendimiento_materias,
        "eventos_proximos": eventos_proximos,
        "ultima_actualizacion": timezone.now(),
        "activity_labels": labels_ultimos,
        "activity_values": values_ultimos,
        "activity_recent_labels": labels_ultimos,
        "activity_recent_values": values_ultimos,
        "asistencia_historial": asistencia_historial_curso,
        "asistencia_totales": totales_asistencia,
        "dias_desde_inicio": dias_desde_inicio,
        "dias_lectivos_contados": dias_lectivos_contados,
        "total_presentes": totales_asistencia["presentes"],
        "total_ausentes": totales_asistencia["ausentes"],
        "asistencia_totales": totales_asistencia,
        "hoy": datetime.now(),
    }

    return render(request, "dashboard/index.html", context)


# ---------------------- VISTAS: AVISOS ----------------------


@login_required
def avisos(request):
    # Mostrar tanto los avisos creados como los recibidos
    creados = Aviso.objects.filter(autor=request.user)
    recibidos = Aviso.objects.filter(destinatarios=request.user)
    lista = (creados | recibidos).distinct().order_by('-fecha_publicacion')
    return render(request, 'dashboard/avisos.html', {'avisos': lista})



@login_required
def crear_aviso(request):
    if request.method == 'POST':
        form = AvisoForm(request.POST)
        if form.is_valid():
            aviso = form.save(commit=False)
            aviso.autor = request.user
            aviso.save()
            form.save_m2m()  # 🔑 guarda los destinatarios seleccionados
            messages.success(request, "✅ Aviso creado correctamente.")
            return redirect('dashboard:avisos')
    else:
        form = AvisoForm()
    return render(request, 'dashboard/crear_aviso.html', {'form': form})



@login_required
def detalle_aviso(request, aviso_id):
    aviso = get_object_or_404(Aviso, id=aviso_id)
    return render(request, 'dashboard/detalle_aviso.html', {'aviso': aviso})


@login_required
def editar_aviso(request, aviso_id):
    aviso = get_object_or_404(Aviso, id=aviso_id)
    if request.user != aviso.autor and not request.user.is_staff:
        return redirect('dashboard:avisos')
    if request.method == 'POST':
        form = AvisoForm(request.POST, instance=aviso)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Aviso modificado.")
            return redirect('dashboard:avisos')
    else:
        form = AvisoForm(instance=aviso)
    return render(request, 'dashboard/editar_aviso.html', {'form': form, 'aviso': aviso})


@login_required
def eliminar_aviso(request, aviso_id):
    aviso = get_object_or_404(Aviso, id=aviso_id)
    if request.user != aviso.autor and not request.user.is_staff:
        return redirect('dashboard:avisos')
    if request.method == "POST":
        aviso.delete()
        messages.success(request, "🗑️ Aviso eliminado.")
        return redirect('dashboard:avisos')
    return render(request, 'dashboard/confirmar_eliminacion_aviso.html', {'aviso': aviso})


# ---------------------- VISTAS: TAREAS ----------------------


@login_required
def tareas(request):
    form = TareaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        tarea = form.save(commit=False)
        tarea.autor = request.user
        tarea.save()
        messages.success(request, "✅ Tarea añadida correctamente.")
        return redirect("dashboard:tareas")
    tareas_qs = Tarea.objects.filter(autor=request.user).order_by("fecha_entrega")
    paginator = Paginator(tareas_qs, 20)
    page = request.GET.get('page')
    tareas_page = paginator.get_page(page)
    return render(request, "dashboard/tareas.html", {"form": form, "tareas": tareas_page})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Tarea
import json

@login_required
def completar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, autor=request.user)
    tarea.completada = True
    tarea.fecha_completado = date.today()
    tarea.save()
    messages.success(request, "✅ Tarea marcada como completada.")
    return redirect("dashboard:tareas_calendario")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Tarea
import json

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Tarea

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Tarea
import json

@login_required
def tareas_calendario(request):
    usuario = request.user
    tareas = Tarea.objects.filter(autor=usuario)

    if request.method == "POST":
        tarea_id = request.POST.get("tarea_id")
        tarea = get_object_or_404(Tarea, id=tarea_id, autor=usuario)
        tarea.completada = True
        tarea.save()
        return redirect("dashboard:tareas_calendario")

    tareas_data = [
        {
            "id": t.id,
            "title": t.titulo,
            "start": t.fecha_entrega.isoformat(),
            "hora": t.hora.strftime("%H:%M") if t.hora else None,
            "descripcion": t.descripcion,
            "completada": t.completada
        }
        for t in tareas
    ]

    return render(request, "dashboard/tareas_calendario.html", {
        "tareas": tareas,
        "tareas_data": tareas_data
    })


    
@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, autor=request.user)
    if request.method == "POST":
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Tarea actualizada.")
            return redirect("dashboard:tareas_calendario")
    else:
        form = TareaForm(instance=tarea)
    return render(request, "dashboard/editar_tarea.html", {"form": form, "tarea": tarea})



@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, autor=request.user)
    if request.method == "POST":
        tarea.delete()
        messages.success(request, "🗑️ Tarea eliminada correctamente.")
        return redirect("dashboard:tareas")
    return render(request, "dashboard/confirmar_eliminacion.html", {"tarea": tarea})


# ---------------------- VISTAS: INCIDENCIAS ----------------------


@login_required
def incidencias_registrar(request):
    if request.method == "POST":
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.autor = request.user
            incidencia.estado = "pendiente"
            incidencia.save()
            messages.success(request, "✅ Incidencia registrada correctamente.")
            return redirect("dashboard:incidencias_listado")
    else:
        form = IncidenciaForm()
    return render(request, "dashboard/incidencias_registrar.html", {"form": form})


@login_required
def incidencias_listado(request):
    incidencias_qs = Incidencia.objects.filter(autor=request.user).order_by("-fecha_reporte")
    pendientes = incidencias_qs.filter(estado="pendiente")
    en_revision = incidencias_qs.filter(estado="revision")
    resueltas = incidencias_qs.filter(estado="resuelta")
    return render(request, "dashboard/incidencias_listado.html", {
        "pendientes": pendientes,
        "en_revision": en_revision,
        "resueltas": resueltas,
    })


@login_required
def panel_incidencias(request):
    pendientes = Incidencia.objects.filter(estado="pendiente").order_by("-fecha_reporte")
    en_revision = Incidencia.objects.filter(estado="revision").order_by("-fecha_reporte")
    resueltas = Incidencia.objects.filter(estado="resuelta").order_by("-fecha_reporte")
    return render(request, "dashboard/incidencias_listado.html", {
        "pendientes": pendientes,
        "en_revision": en_revision,
        "resueltas": resueltas
    })


@login_required
def cambiar_estado_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    if request.method == 'POST':
        form = EstadoIncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Estado de la incidencia actualizado.")
            return redirect('dashboard:incidencias_listado')
    else:
        form = EstadoIncidenciaForm(instance=incidencia)
    return render(request, 'dashboard/cambiar_estado.html', {'form': form, 'incidencia': incidencia})


@login_required
def marcar_resuelta(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    if request.user != incidencia.autor and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para modificar esta incidencia.")
    incidencia.estado = "resuelta"
    incidencia.fecha_resolucion = timezone.now()
    incidencia.save()
    messages.success(request, "✅ Incidencia marcada como resuelta.")
    return redirect('dashboard_home')


@user_passes_test(lambda u: u.is_staff)
@login_required
def moderador_incidencias(request):
    incidencias = Incidencia.objects.all().order_by("-fecha_reporte")
    return render(request, "dashboard/moderador_incidencias.html", {"incidencias": incidencias})


# ---------------------- VISTAS: MENSAJES / CHAT ----------------------


@login_required
def mensajes(request):
    return render(request, "dashboard/mensajes.html")


@login_required
def inbox(request):
    mensajes = PrivateMessage.objects.filter(
        receiver=request.user,
        is_read=False
    ).order_by("-created_at")
    return render(request, "dashboard/inbox.html", {"mensajes": mensajes})



@login_required
def outbox(request):
    mensajes_qs = PrivateMessage.objects.filter(sender=request.user).order_by("-created_at")
    paginator = Paginator(mensajes_qs, 20)
    page = request.GET.get('page')
    mensajes_page = paginator.get_page(page)
    return render(request, "dashboard/outbox.html", {"mensajes": mensajes_page})


@login_required
def chat(request, usuario_id):
    other_user = get_object_or_404(CustomUser, id=usuario_id)
    contacts = CustomUser.objects.exclude(id=request.user.id)
    if request.method == "POST":
        content = request.POST.get("message")
        if content:
            PrivateMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                subject="(chat directo)",
                is_read=False
            )
            return redirect("dashboard:chat", usuario_id=usuario_id)
    messages_qs = PrivateMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("created_at")
    return render(request, "dashboard/chat.html", {
        "contacts": contacts,
        "messages": messages_qs,
        "other_user": other_user
    })


@login_required
def send_message(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        subject = request.POST.get("subject", "")
        content = request.POST.get("content", "")
        if receiver_id and content:
            receiver = get_object_or_404(User, id=receiver_id)
            PrivateMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                subject=subject,
                content=content,
                is_read=False
            )
            messages.success(request, "✅ Mensaje enviado correctamente.")
            return redirect("dashboard:outbox")
        else:
            messages.error(request, "❌ Faltan datos para enviar el mensaje.")
            return redirect("dashboard:mensajes")
    return redirect("dashboard:mensajes")


# ---------------------- VISTAS: ANUNCIOS ----------------------


@login_required
def latest_announcements(request):
    announcements = Announcement.objects.order_by("-created_at")[:10]
    return render(request, "dashboard/latest_announcements.html", {"announcements": announcements})


@login_required
def mark_all_as_read(request):
    unread = AnnouncementRead.objects.filter(user=request.user, read_at__isnull=True)
    unread.update(read_at=timezone.now())
    messages.success(request, "✅ Todos los anuncios marcados como leídos.")
    return redirect("dashboard:latest_announcements")


@login_required
def export_announcements_excel(request):
    # Placeholder: implementa según librería preferida (openpyxl / pandas / xlsxwriter)
    return HttpResponse("Exportación no implementada aún.")


# ---------------------- VISTAS: OTROS / NOTIFICACIONES / PERFIL ----------------------


@login_required
def latest_notifications(request):
    notifs = Notification.objects.filter(user=request.user).order_by("-creado")[:20]
    data = [
        {
            "id": n.id,
            "tipo": n.tipo,
            "titulo": n.titulo,
            "contenido": n.contenido,
            "url": n.url,
            "leido": n.leido,
            "creado": n.creado.strftime("%d/%m/%Y %H:%M")
        }
        for n in notifs
    ]
    return JsonResponse({"notificaciones": data})


@require_POST
def marcar_notificaciones_leidas(request):
    Notification.objects.filter(user=request.user, leida=False).update(leida=True)
    return JsonResponse({"success": True})


@login_required
def configuracion(request):
    return render(request, "dashboard/configuracion.html")


@login_required
def compose_message(request):
    if request.method == "POST":
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()

            Notification.objects.create(
                user=msg.receiver,
                tipo="info",
                titulo="Nuevo mensaje privado",
                contenido=f"Has recibido un mensaje de {request.user.username}: {msg.subject}",
                url = reverse("dashboard:mensaje_detalle", args=[msg.id]),
                mensaje=msg
            )

            messages.success(request, "Mensaje enviado correctamente ✅")
            return redirect("dashboard:outbox")
    else:
        form = PrivateMessageForm()
    return render(request, "dashboard/mensajes.html", {"form": form})


@login_required
def mensaje_detalle(request, pk):
    mensaje = get_object_or_404(PrivateMessage, pk=pk, receiver=request.user)
    return render(request, "dashboard/mensaje_detalle.html", {"mensaje": mensaje})


@require_POST
@login_required
def toggle_read(request, mensaje_id):
    msg = get_object_or_404(PrivateMessage, id=mensaje_id)
    if msg.receiver_id != request.user.id:
        return HttpResponseForbidden("Not allowed")
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    return HttpResponse(status=204)


@login_required
def reply(request, pk):
    mensaje = get_object_or_404(PrivateMessage, pk=pk, receiver=request.user)
    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        if content:
            PrivateMessage.objects.create(
                sender=request.user,
                receiver=mensaje.sender,
                subject=f"Re: {mensaje.subject}" if mensaje.subject else "Re:",
                content=content,
            )
            # Opcional: marcar el original como leído
            mensaje.is_read = True
            mensaje.save()
        return redirect("dashboard:mensaje_detalle", pk=pk)
    # En GET, vuelve al detalle (no necesitas renderizar reply.html)
    return redirect("dashboard:mensaje_detalle", pk=pk)


# ---------------------- UTILIDADES / DEBUG / BACKUPS ----------------------

# Si quieres añadir endpoints de depuración (solo en desarrollo), añádelos aquí.
# Ejemplo: una vista que devuelva JSON con el contexto del dashboard (solo staff).
@login_required
@user_passes_test(lambda u: u.is_staff)
def debug_dashboard_context(request):
    """
    Devuelve una snapshot JSON del contexto del dashboard para debugging.
    WARNING: solo staff.
    """
    user = request.user
    tareas_qs = Tarea.objects.filter(autor=user)
    context = {
        "total_tareas": tareas_qs.count(),
        "tareas_completadas": tareas_qs.filter(completada=True).count(),
        "hoy": date.today().isoformat(),
        "es_lectivo": es_dia_lectivo(date.today())[0],
    }
    return JsonResponse(context)


def test_calendario(request):
    return render(request, "dashboard/calendario_test.html")
