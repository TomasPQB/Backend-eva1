# Plan: sistema de reservas de canchas

## Problema y solución

El registro manual de reservas dificulta conocer la disponibilidad y conservar un
historial confiable. La aplicación permite registrar solicitudes, aplicar la regla
de negocio existente, consultar resultados y administrar las reservas con acceso
por usuario y rol.

## Alcance entregado

- SQLite guarda las reservas mediante el ORM de Django.
- `solucion.py` conserva la función `decidir_reserva()` original; las vistas la
  reutilizan y no duplican sus reglas.
- El CRUD web ofrece listar, crear, editar y eliminar lógicamente reservas.
- Los grupos `admin`, `normal` y `viewer` definen los permisos de la aplicación.
- Django Admin permite buscar, filtrar y gestionar las reservas.
- Login, cierre de sesión por POST, sesiones Django, CSRF, validación de formularios
  y contraseñas almacenadas mediante el sistema de autenticación de Django.
- `datos.json` se conserva para el ejercicio original, pero la aplicación web usa
  SQLite como fuente de datos.

## Priorización MoSCoW

- **Must:** base de datos y migraciones, regla de decisión existente, CRUD, login,
  sesiones y permisos por rol.
- **Should:** administrador personalizado, borrado lógico y pruebas de validación
  y acceso.
- **Could:** informes y filtros de consulta adicionales.
- **Won't:** crear un sistema propio de contraseñas o duplicar la regla de negocio.

## Preparar una copia limpia (Windows PowerShell)

1. Crear y activar un entorno, e instalar dependencias:

   ```powershell
   py -m venv env
   .\env\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Crear el archivo privado de configuración:

   ```powershell
   Copy-Item .env.example .env
   ```

   Completar `.env` localmente: generar `SECRET_KEY` con
   `python -c "import secrets; print(secrets.token_urlsafe(50))"`, configurar
   `DEBUG=True`, `ALLOWED_HOSTS=localhost,127.0.0.1` y definir nombres de usuario
   distintos junto con contraseñas únicas y fuertes para los tres roles. No
   compartir ni subir `.env`.

3. Crear las tablas y verificar que los modelos estén sincronizados:

   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   python manage.py makemigrations --check --dry-run
   ```

4. Crear los grupos y usuarios de la aplicación a partir de las credenciales
   configuradas en `.env`:

   ```powershell
   python manage.py setup_roles
   ```

   El comando valida las contraseñas con los validadores de Django y sincroniza
   las contraseñas con los valores privados del entorno cada vez que se ejecuta.
   El usuario del grupo `admin` puede gestionar reservas en `/admin/`; `normal`
   puede crear y consultar reservas, y `viewer` solo puede consultarlas.

5. Ejecutar las pruebas, iniciar el servidor y abrir la aplicación:

   ```powershell
   python manage.py test core
   python manage.py runserver
   ```

   Las pruebas usan una base temporal e incluyen datos de prueba, validaciones,
   CSRF, login/logout, acceso directo a URL protegidas y borrado lógico.

## Configuración para producción

No usar `DEBUG=True`. Definir `ALLOWED_HOSTS` con los dominios reales y servir la
aplicación exclusivamente por HTTPS: con `DEBUG=False`, Django activa la redirección
a HTTPS y las cookies de sesión y CSRF seguras. No incluir `db.sqlite3`, `.env` ni
contraseñas reales en el repositorio.

## Datos y seguridad

Los campos de la reserva se validan antes de guardar; el estado y el motivo se
recalculan tanto al crear como al editar. Las vistas verifican autenticación y rol
en el servidor, no solo ocultan botones en las plantillas. El borrado lógico conserva
el historial y excluye las reservas eliminadas de las consultas de la aplicación.
