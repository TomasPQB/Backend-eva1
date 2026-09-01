from django.urls import path

from .views import resumen

urlpatterns = [
    path('', resumen, name='resumen'),
]
