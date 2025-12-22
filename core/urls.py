from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("usuarios/registro/", views.registro, name="registro"),
    path("perfil/", views.perfil_view, name="perfil"),                # perfil propio
    path("perfil/<int:user_id>/", views.perfil_usuario, name="perfil_usuario"),  # perfil por ID
    path("usuarios/editar/", views.editar_perfil, name="editar_perfil"),
]
