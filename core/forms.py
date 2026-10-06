from django import forms

from .models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ("nombre", "horas")
        labels = {"nombre": "Nombre", "horas": "Horas"}
        widgets = {
            "nombre": forms.TextInput(attrs={"maxlength": 100, "required": True}),
            "horas": forms.NumberInput(attrs={"required": True}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("Escribe el nombre de la persona.")
        return nombre
