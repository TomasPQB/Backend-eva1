from rest_framework import viewsets

from .models import Reserva
from .permissions import ReservaAPIPermission
from .serializers import ReservaSerializer
from .services import resultado_reserva


class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = (ReservaAPIPermission,)
    queryset = Reserva.objects.filter(eliminado=False).order_by("-fecha")
    search_fields = ("nombre", "estado")
    ordering_fields = ("fecha", "nombre", "horas", "estado")
    ordering = ("-fecha",)

    def perform_create(self, serializer):
        estado, motivo = resultado_reserva(
            serializer.validated_data["nombre"],
            serializer.validated_data["horas"],
        )
        serializer.save(estado=estado, motivo=motivo)

    def perform_update(self, serializer):
        reserva = serializer.instance
        nombre = serializer.validated_data.get("nombre", reserva.nombre)
        horas = serializer.validated_data.get("horas", reserva.horas)
        estado, motivo = resultado_reserva(
            nombre,
            horas,
            reserva_id=reserva.pk,
        )
        serializer.save(estado=estado, motivo=motivo)

    def perform_destroy(self, instance):
        instance.soft_delete()
