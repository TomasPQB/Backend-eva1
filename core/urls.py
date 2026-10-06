from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html", next_page="lista"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("reservas/crear/", views.crear, name="crear"),
    path("reservas/<int:pk>/editar/", views.editar, name="editar"),
    path("reservas/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
