# colegio_1/announcements/views.py
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Announcement
from .filters import AnnouncementFilter
from schoolcomms.utils.email import send_announcement_email
from schoolcomms.dashboard.models import NotificationPreference
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from schoolcomms.dashboard.models import NotificationPreference

def announcement_list(request):
    """
    Lista de avisos con filtros (django-filter) y paginación.
    Renderiza template: 'announcements/index.html'
    """
    qs = Announcement.objects.all().order_by('-created_at')

    # Aplicar filtros
    filterset = AnnouncementFilter(request.GET, queryset=qs)
    qs_filtered = filterset.qs

    # Paginación (10 por página, cámbialo si quieres)
    paginator = Paginator(qs_filtered, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Contadores para las tarjetas del dashboard
    announcements_count = qs_filtered.count()

    # unread_count: ejemplo seguro (si tienes modelo ReadReceipt lo usarás)
    # Evitamos que falle si no existe ese modelo
    unread_count = 0
    try:
        # si tienes un modelo ReadReceipt o Receipt, ajústalo aquí
        from .models import ReadReceipt
        unread_count = ReadReceipt.objects.filter(user=request.user, read=False).count()
    except Exception:
        unread_count = 0

    # tasks_count: si usas django-celery-results (opcional)
    try:
        from django_celery_results.models import TaskResult
        tasks_count = TaskResult.objects.count()
    except Exception:
        tasks_count = 0

    context = {
        'filterset': filterset,
        'page_obj': page_obj,
        'paginator': paginator,
        'announcements_count': announcements_count,
        'unread_count': unread_count,
        'tasks_count': tasks_count,
    }

    return render(request, 'announcements/index.html', context)

def export_announcements_pdf(request):
    from .models import Announcement
    announcements = Announcement.objects.all().order_by('-created_at')

    template = get_template("announcements/pdf_template.html")
    html = template.render({"announcements": announcements})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=avisos.pdf"

    pisa_status = pisa.CreatePDF(html, dest=response)
    return response if not pisa_status.err else HttpResponse("Error al generar PDF", status=500)


User = get_user_model()


def crear_aviso(request):
    aviso = Announcement.objects.create(...)  # tu lógica de creación

    usuarios = User.objects.filter(groups__in=aviso.target_groups.all()).distinct()

    for user in usuarios:
        prefs = getattr(user, "notificationpreference", None)
        if prefs and prefs.email_enabled and prefs.notify_on_announcement:
            html = render_to_string("emails/aviso.html", {"aviso": aviso, "usuario": user})
            send_announcement_email(user.email, f"📢 Nuevo aviso: {aviso.title}", html)