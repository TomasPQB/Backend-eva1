from .models import Reserva
from solucion import TOTAL_CANCHAS, decidir_reserva


def resultado_reserva(nombre, horas, *, reserva_id=None):
    reservas_aceptadas = Reserva.objects.filter(
        eliminado=False, estado="Reserva aceptada"
    )
    if reserva_id is not None:
        reservas_aceptadas = reservas_aceptadas.exclude(pk=reserva_id)
    canchas_disponibles = TOTAL_CANCHAS - reservas_aceptadas.count()
    return decidir_reserva(nombre, horas, canchas_disponibles)
