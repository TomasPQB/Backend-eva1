from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase
from django.urls import reverse

from core.admin import ReservaAdminForm
from core.models import Reserva
from solucion import decidir_reserva

User = get_user_model()


def crear_reserva(nombre="Ana", horas=1, estado="Reserva aceptada"):
    return Reserva.objects.create(
        nombre=nombre,
        horas=horas,
        estado=estado,
        motivo="La solicitud cumple las condiciones.",
    )


class ReservaModelTest(TestCase):
    def test_decidir_reserva_reutiliza_logica(self):
        estado, motivo = decidir_reserva("Ana", 1, 2)
        self.assertEqual(estado, "Reserva aceptada")
        self.assertIn("cumple", motivo)

    def test_crear_reserva_guarda_en_bd(self):
        reserva = crear_reserva(nombre="Luis")
        self.assertEqual(Reserva.objects.count(), 1)
        self.assertEqual(Reserva.objects.get(), reserva)

    def test_borrado_logico_conserva_el_registro(self):
        reserva = crear_reserva()
        reserva.soft_delete()
        reserva.refresh_from_db()
        self.assertTrue(reserva.eliminado)
        self.assertIsNotNone(reserva.fecha_eliminacion)
        self.assertEqual(Reserva.objects.count(), 1)

    def test_regla_de_negocio_marca_horas_no_validas(self):
        reserva = crear_reserva(horas=0, estado="Dato inválido")
        estado, motivo = decidir_reserva(reserva.nombre, reserva.horas, 3)
        self.assertEqual(estado, "Dato inválido")
        self.assertIn("mayor que cero", motivo)

    def test_formulario_del_admin_valida_el_nombre(self):
        form = ReservaAdminForm(
            data={
                "nombre": "   ",
                "horas": "1",
                "estado": "Reserva aceptada",
                "motivo": "Motivo",
                "eliminado": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nombre", form.errors)


class ReservaAccessTest(TestCase):
    def setUp(self):
        self.admin_group, _ = Group.objects.get_or_create(name="admin")
        self.admin_group.permissions.set(
            Permission.objects.filter(content_type__app_label="core")
        )
        self.normal_group, _ = Group.objects.get_or_create(name="normal")
        self.viewer_group, _ = Group.objects.get_or_create(name="viewer")

        self.admin = User.objects.create_user(
            username="admin_test",
            password="Test-Only-Password-2026!",
            is_staff=True,
        )
        self.admin.groups.add(self.admin_group)
        self.normal = User.objects.create_user(
            username="normal_test", password="Test-Only-Password-2026!"
        )
        self.normal.groups.add(self.normal_group)
        self.viewer = User.objects.create_user(
            username="viewer_test", password="Test-Only-Password-2026!"
        )
        self.viewer.groups.add(self.viewer_group)

    def test_visitante_es_redirigido_al_login(self):
        response = self.client.get(reverse("lista"))
        self.assertRedirects(response, f"{reverse('login')}?next=/")

    def test_admin_puede_entrar_a_django_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get("/admin/core/reserva/")
        self.assertEqual(response.status_code, 200)

    def test_viewer_no_puede_entrar_a_django_admin(self):
        self.client.force_login(self.viewer)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)

    def test_normal_puede_crear_y_ve_el_boton(self):
        self.client.force_login(self.normal)
        response = self.client.get(reverse("lista"))
        self.assertContains(response, reverse("crear"))
        response = self.client.post(
            reverse("crear"), {"nombre": "Ana", "horas": "1"}
        )
        self.assertRedirects(response, reverse("lista"))
        reserva = Reserva.objects.get()
        self.assertEqual(reserva.nombre, "Ana")
        self.assertEqual(reserva.estado, "Reserva aceptada")

    def test_login_crea_una_sesion_autenticada(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.normal.username,
                "password": "Test-Only-Password-2026!",
            },
        )
        self.assertRedirects(response, reverse("lista"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_horas_cero_se_guarda_con_el_resultado_de_la_regla(self):
        self.client.force_login(self.normal)
        response = self.client.post(
            reverse("crear"), {"nombre": "Caso inválido", "horas": "0"}
        )
        self.assertRedirects(response, reverse("lista"))
        reserva = Reserva.objects.get()
        self.assertEqual(reserva.estado, "Dato inválido")
        self.assertIn("mayor que cero", reserva.motivo)

    def test_formulario_rechaza_nombre_vacio_horas_invalidas_y_largas(self):
        self.client.force_login(self.normal)
        url = reverse("crear")
        casos_invalidos = (
            {"nombre": "   ", "horas": "1"},
            {"nombre": "Ana", "horas": "dos"},
            {"nombre": "A" * 101, "horas": "1"},
        )
        for datos in casos_invalidos:
            with self.subTest(datos=datos):
                response = self.client.post(url, datos)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Reserva.objects.count(), 0)

    def test_viewer_no_puede_crear_editar_ni_eliminar(self):
        reserva = crear_reserva()
        self.client.force_login(self.viewer)
        self.assertRedirects(
            self.client.get(reverse("crear")), reverse("lista")
        )
        self.assertRedirects(
            self.client.get(reverse("editar", args=[reserva.pk])),
            reverse("lista"),
        )
        self.assertRedirects(
            self.client.post(reverse("eliminar", args=[reserva.pk])),
            reverse("lista"),
        )
        reserva.refresh_from_db()
        self.assertFalse(reserva.eliminado)

    def test_normal_no_puede_editar_ni_eliminar_por_url_directa(self):
        reserva = crear_reserva()
        self.client.force_login(self.normal)
        self.assertRedirects(
            self.client.post(
                reverse("editar", args=[reserva.pk]),
                {"nombre": "Cambio", "horas": "1"},
            ),
            reverse("lista"),
        )
        self.assertRedirects(
            self.client.post(reverse("eliminar", args=[reserva.pk])),
            reverse("lista"),
        )
        reserva.refresh_from_db()
        self.assertEqual(reserva.nombre, "Ana")
        self.assertFalse(reserva.eliminado)

    def test_admin_edita_y_elimina_sin_borrar_historico(self):
        reserva = crear_reserva()
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("editar", args=[reserva.pk]),
            {"nombre": "Ana María", "horas": "2"},
        )
        self.assertRedirects(response, reverse("lista"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.nombre, "Ana María")

        response = self.client.post(
            reverse("editar", args=[reserva.pk]),
            {"nombre": "Ana María", "horas": "3"},
        )
        self.assertRedirects(response, reverse("lista"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, "Reserva rechazada")
        self.assertIn("dos horas", reserva.motivo)

        response = self.client.post(reverse("eliminar", args=[reserva.pk]))
        self.assertRedirects(response, reverse("lista"))
        reserva.refresh_from_db()
        self.assertTrue(reserva.eliminado)

    def test_logout_requiere_post_y_finaliza_la_sesion(self):
        self.client.force_login(self.normal)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_csrf_rechaza_post_sin_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.normal)
        response = client.post(
            reverse("crear"), {"nombre": "Ana", "horas": "1"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Reserva.objects.count(), 0)


class SetupRolesCommandTest(TestCase):
    def test_crea_roles_usuarios_y_sincroniza_contrasenas_del_entorno(self):
        variables = {
            "ADMIN_USER": "equipo_admin",
            "ADMIN_PASSWORD": "T3j0n!Bruma-47-Menta",
            "NORMAL_USER": "equipo_normal",
            "NORMAL_PASSWORD": "C0bre!Nube-82-Bosque",
            "VIEWER_USER": "equipo_viewer",
            "VIEWER_PASSWORD": "Lun4!Risco-63-Cedro",
        }
        with patch(
            "core.management.commands.setup_roles.config",
            side_effect=lambda key, default=None: variables.get(key, default),
        ):
            call_command("setup_roles", verbosity=0)

        admin_user = User.objects.get(username="equipo_admin")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.check_password(variables["ADMIN_PASSWORD"]))
        self.assertTrue(admin_user.groups.filter(name="admin").exists())
        self.assertTrue(
            admin_user.groups.get(name="admin").permissions.filter(
                content_type__app_label="core"
            ).exists()
        )
        self.assertTrue(admin_user.has_perm("core.view_reserva"))
        self.assertFalse(User.objects.get(username="equipo_normal").is_staff)
        self.assertFalse(
            User.objects.get(username="equipo_normal").has_perm(
                "core.change_reserva"
            )
        )

        variables["ADMIN_PASSWORD"] = "P4sto!Cielo-71-Cuarzo"
        with patch(
            "core.management.commands.setup_roles.config",
            side_effect=lambda key, default=None: variables.get(key, default),
        ):
            call_command("setup_roles", verbosity=0)
        admin_user.refresh_from_db()
        self.assertTrue(admin_user.check_password(variables["ADMIN_PASSWORD"]))

    def test_falla_con_credenciales_ausentes(self):
        with patch(
            "core.management.commands.setup_roles.config",
            side_effect=lambda key, default=None: "",
        ):
            with self.assertRaises(CommandError):
                call_command("setup_roles", verbosity=0)
