from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import cambiar_estado_incidencia

app_name = "dashboard"

urlpatterns = [
    # Página principal
    path("", login_required(views.dashboard_home), name="inicio"),

    # Avisos personales
    path("avisos/", login_required(views.avisos), name="avisos"),
    path("avisos/crear/", login_required(views.crear_aviso), name="crear_aviso"),
    path("avisos/<int:aviso_id>/", login_required(views.detalle_aviso), name="detalle_aviso"),
    path("avisos/<int:aviso_id>/editar/", login_required(views.editar_aviso), name="editar_aviso"),
    path("avisos/<int:aviso_id>/eliminar/", login_required(views.eliminar_aviso), name="eliminar_aviso"),

    
    # Tareas escolares
    path("tareas/", login_required(views.tareas), name="tareas"),
    path("tareas/calendario/", login_required(views.tareas_calendario), name="tareas_calendario"),
    path("tareas/editar/<int:tarea_id>/", login_required(views.editar_tarea), name="editar_tarea"),
    path("tareas/eliminar/<int:tarea_id>/", login_required(views.eliminar_tarea), name="eliminar_tarea"),
    path("tareas/completar/<int:tarea_id>/", login_required(views.completar_tarea), name="completar_tarea"),
    path("tareas/test/calendario/", login_required(views.test_calendario), name="test_calendario"),


    # Incidencias
    path("incidencias/", login_required(views.incidencias_listado), name="incidencias_listado"),
    path("incidencias/registrar/", login_required(views.incidencias_registrar), name="incidencias_registrar"),
    path("incidencias/panel/", login_required(views.panel_incidencias), name="panel_incidencias"),
    path("incidencias/<int:incidencia_id>/resuelta/", login_required(views.marcar_resuelta), name="marcar_resuelta"),
    path("incidencias/moderador/", login_required(views.moderador_incidencias), name="moderador_incidencias"),
    path("incidencias/<int:pk>/estado/", login_required(cambiar_estado_incidencia), name="cambiar_estado_incidencia"),

    # Mensajes privados
    path("mensajes/", login_required(views.compose_message), name="compose_message"),
    path("mensajes/inbox/", login_required(views.inbox), name="inbox"),
    path("mensajes/outbox/", login_required(views.outbox), name="outbox"),
    path("mensajes/chat/<int:usuario_id>/", login_required(views.chat), name="chat"),
    path("mensajes/enviar/", login_required(views.send_message), name="send_message"),
    path("mensajes/<int:pk>/", login_required(views.mensaje_detalle), name="mensaje_detalle"),
    path("notificaciones/marcar-todas/", login_required(views.marcar_notificaciones_leidas), name="marcar_notificaciones"),
    path("mensajes/toggle-read/<int:pk>/", views.toggle_read, name="toggle_read"),
    path("mensajes/reply/<int:pk>/", views.reply, name="reply"),
    path("mensajes/<int:mensaje_id>/toggle-read/", views.toggle_read, name="toggle_read"),

    # Anuncios institucionales
    path("anuncios/recientes/", login_required(views.latest_announcements), name="latest_announcements"),
    path("anuncios/marcar-todos-leidos/", login_required(views.mark_all_as_read), name="mark_all_as_read"),
    path("anuncios/exportar/", login_required(views.export_announcements_excel), name="export_announcements"),

    # Configuración
    path("configuracion/", login_required(views.configuracion), name="configuracion"),
]
