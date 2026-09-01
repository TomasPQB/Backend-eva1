from django.shortcuts import render

from solucion import (
    TOTAL_CANCHAS,
    cargar_registros,
    guardar_registros,
    registrar_reserva,
)


def resumen(request):
    registro = None
    error = None

    if request.method == "POST":
        if request.POST.get("accion") == "borrar":
            guardar_registros([])
        else:
            nombre = request.POST.get("nombre", "").strip()
            horas_texto = request.POST.get("horas", "").strip()
            if not nombre:
                error = "Escribe el nombre de la persona."
            else:
                try:
                    horas = int(horas_texto)
                except ValueError:
                    error = "La cantidad de horas debe ser un número entero."
                else:
                    registro, _ = registrar_reserva(nombre, horas)

    registros = cargar_registros()
    canchas_ocupadas = sum(
        registro["estado"] == "Reserva aceptada" for registro in registros
    )
    canchas_disponibles = max(TOTAL_CANCHAS - canchas_ocupadas, 0)

    return render(
        request,
        "core/resumen.html",
        {
            "registros": registros,
            "registro": registro,
            "error": error,
            "canchas_disponibles": canchas_disponibles,
            "total_canchas": TOTAL_CANCHAS,
        },
    )
