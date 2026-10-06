from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from solucion import TOTAL_CANCHAS, decidir_reserva

from .forms import ReservaForm
from .models import Reserva


def tiene_rol(user, *roles):
    return user.is_superuser or user.groups.filter(name__in=roles).exists()


def requiere_rol(*roles):
    def decorador(view_func):
        @wraps(view_func)
        @login_required(login_url="login")
        def wrapper(request, *args, **kwargs):
            if tiene_rol(request.user, *roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para esta acción.")
            return redirect("lista")

        return wrapper

    return decorador


def _guardar_reserva(form):
    reserva = form.save(commit=False)
    reservas_aceptadas = Reserva.objects.filter(
        eliminado=False, estado="Reserva aceptada"
    )
    if reserva.pk:
        reservas_aceptadas = reservas_aceptadas.exclude(pk=reserva.pk)
    canchas_disponibles = TOTAL_CANCHAS - reservas_aceptadas.count()
    reserva.estado, reserva.motivo = decidir_reserva(
        reserva.nombre, reserva.horas, canchas_disponibles
    )
    reserva.save()
    return reserva


@login_required(login_url="login")
def lista(request):
    reservas = Reserva.objects.filter(eliminado=False)
    canchas_ocupadas = reservas.filter(estado="Reserva aceptada").count()
    canchas_disponibles = max(TOTAL_CANCHAS - canchas_ocupadas, 0)
    es_admin = tiene_rol(request.user, "admin")
    puede_crear = tiene_rol(request.user, "admin", "normal")

    return render(
        request,
        "core/lista.html",
        {
            "reservas": reservas,
            "canchas_disponibles": canchas_disponibles,
            "total_canchas": TOTAL_CANCHAS,
            "es_admin": es_admin,
            "puede_crear": puede_crear,
        },
    )


@requiere_rol("admin", "normal")
def crear(request):
    form = ReservaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        _guardar_reserva(form)
        messages.success(request, "Reserva registrada correctamente.")
        return redirect("lista")

    return render(
        request,
        "core/form.html",
        {"accion": "Crear", "form": form, "es_admin": tiene_rol(request.user, "admin")},
    )


@requiere_rol("admin")
def editar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk, eliminado=False)
    form = ReservaForm(request.POST or None, instance=reserva)
    if request.method == "POST" and form.is_valid():
        _guardar_reserva(form)
        messages.success(request, "Reserva actualizada correctamente.")
        return redirect("lista")

    return render(
        request,
        "core/form.html",
        {
            "accion": "Editar",
            "form": form,
            "es_admin": tiene_rol(request.user, "admin"),
        },
    )


@requiere_rol("admin")
def eliminar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk, eliminado=False)

    if request.method == "POST":
        reserva.soft_delete()
        messages.success(request, "Reserva eliminada correctamente.")
        return redirect("lista")

    return render(
        request,
        "core/confirm_delete.html",
        {"reserva": reserva, "es_admin": tiene_rol(request.user, "admin")},
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")
