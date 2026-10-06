from django import forms
from django.contrib import admin

from .models import Reserva


class ReservaAdminForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre no puede quedar vacío.")
        return nombre


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    form = ReservaAdminForm
    list_display = (
        "nombre",
        "horas",
        "estado",
        "motivo",
        "fecha",
        "eliminado",
        "fecha_eliminacion",
    )
    list_filter = ("estado", "eliminado")
    search_fields = ("nombre",)
    readonly_fields = ("fecha_eliminacion",)

    def delete_model(self, request, obj):
        obj.soft_delete()

    def delete_queryset(self, request, queryset):
        for reserva in queryset:
            reserva.soft_delete()
