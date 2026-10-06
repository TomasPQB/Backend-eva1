from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Crea grupos y sincroniza usuarios desde las variables de entorno"

    def handle(self, *args, **options):
        usuarios = (
            (
                config("ADMIN_USER", default="").strip(),
                "admin",
                config("ADMIN_PASSWORD", default=""),
                True,
            ),
            (
                config("NORMAL_USER", default="").strip(),
                "normal",
                config("NORMAL_PASSWORD", default=""),
                False,
            ),
            (
                config("VIEWER_USER", default="").strip(),
                "viewer",
                config("VIEWER_PASSWORD", default=""),
                False,
            ),
        )

        if any(not username or not password for username, _, password, _ in usuarios):
            raise CommandError(
                "Define los tres usuarios y sus contraseñas en el archivo .env."
            )
        usernames = [username for username, _, _, _ in usuarios]
        if len(set(usernames)) != len(usernames):
            raise CommandError("Cada rol debe tener un nombre de usuario distinto.")

        User = get_user_model()
        with transaction.atomic():
            grupos = {
                nombre: Group.objects.get_or_create(name=nombre)[0]
                for nombre in ("admin", "normal", "viewer")
            }
            grupos["admin"].permissions.set(
                Permission.objects.filter(content_type__app_label="core")
            )

            for username, nombre_grupo, password, es_staff in usuarios:
                user, _ = User.objects.get_or_create(username=username)
                try:
                    validate_password(password, user=user)
                except ValidationError as error:
                    raise CommandError(
                        f"La contraseña configurada para {username} no es segura: "
                        + " ".join(error.messages)
                    ) from error

                user.set_password(password)
                user.is_staff = user.is_superuser or es_staff
                user.groups.set([grupos[nombre_grupo]])
                user.save()

        self.stdout.write(
            self.style.SUCCESS("Grupos y usuarios configurados correctamente.")
        )
