from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from schoolcomms import views as core_views
from schoolcomms.dashboard import views as dashboard_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Redirección raíz al dashboard (requiere sesión iniciada)
@login_required
def root_redirect(request):
    return redirect("dashboard:inicio")

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Raíz → dashboard inicio
    path("", root_redirect),

    # Dashboard (namespace)
    path("dashboard/", include(("schoolcomms.dashboard.urls", "dashboard"), namespace="dashboard")),

    # Login
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),

    # Logout (pantalla personalizada)
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # Password reset (flujo completo con plantillas de email y success_url)
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            email_template_name="registration/password_reset_email.txt",
            html_email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url="/accounts/password_reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # Usuarios (perfil, edición, registro) con namespace
    path("usuarios/", include(("core.urls", "core"), namespace="core")),

    # Announcements (namespace)
    path("announcements/", include(("announcements.urls", "announcements"), namespace="announcements")),

    # Test email (si lo usas para probar envío)
    path("test-email/", core_views.test_sendgrid_email, name="test_email"),

    # Incidencias (si no está duplicado en dashboard.urls, puedes eliminar esta línea)
    path("incidencias/", dashboard_views.incidencias_listado, name="incidencias_listado"),

    # Favicon
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
]

# Archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
