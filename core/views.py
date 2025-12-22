from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PerfilForm, RegistroForm

User = get_user_model()


def registro(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "✅ Cuenta creada correctamente. Ya puedes iniciar sesión.")
            return redirect("login")
        else:
            messages.error(request, "❌ Revisa los campos del formulario. Hay errores que corregir.")
    else:
        form = RegistroForm()
    return render(request, "registration/registro.html", {"form": form})


@login_required
def editar_perfil(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente.")
            return redirect("core:perfil_usuario", user_id=request.user.id)
        else:
            messages.error(request, "❌ No se pudo actualizar el perfil. Revisa los errores.")
    else:
        form = PerfilForm(instance=request.user)
    return render(request, "core/editar_perfil.html", {"form": form})


@login_required
def perfil_view(request: HttpRequest) -> HttpResponse:
    """Perfil del usuario autenticado"""
    return render(request, "core/perfil.html", {"usuario": request.user})


@login_required
def perfil_usuario(request: HttpRequest, user_id: int) -> HttpResponse:
    """Perfil público/básico de otro usuario"""
    usuario = get_object_or_404(User, pk=user_id)
    return render(request, "core/perfil.html", {"usuario": usuario})
