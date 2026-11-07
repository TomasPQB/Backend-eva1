from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReservaAPIPermission(BasePermission):
    message = "Tu rol no tiene permiso para esta operación."

    def has_permission(self, request, _view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return (
                user.is_superuser
                or user.is_staff
                or user.groups.filter(name__in=("admin", "normal")).exists()
            )
        if request.method in ("PUT", "PATCH", "DELETE"):
            return (
                user.is_superuser
                or user.is_staff
                or user.groups.filter(name="admin").exists()
            )
        return False
