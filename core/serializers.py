from rest_framework import serializers

from .models import Reserva


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ("id", "nombre", "horas", "estado", "motivo", "fecha")
        read_only_fields = ("id", "estado", "motivo", "fecha")

    def validate_nombre(self, valor):
        nombre = valor.strip()
        if not nombre:
            raise serializers.ValidationError(
                "Escribe el nombre de la persona."
            )
        return nombre
