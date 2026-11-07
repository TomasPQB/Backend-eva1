# Sistema de reservas y API REST

El proyecto conserva las pantallas HTML de ES2 y añade una API JSON con Django
REST Framework. Ambas interfaces trabajan sobre las mismas reservas, la misma
base SQLite y la misma regla `decidir_reserva()`.

## Preparación

En Windows PowerShell, activa el entorno e instala las dependencias:

```powershell
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Completa `.env` localmente con una `SECRET_KEY` aleatoria (por ejemplo,
`python -c "import secrets; print(secrets.token_urlsafe(50))"`), `DEBUG=True`
para desarrollo y credenciales propias para los roles. No compartas ese archivo.
Después prepara la base y los usuarios:

```powershell
python manage.py migrate
python manage.py setup_roles
python manage.py runserver
```

`setup_roles` crea los grupos `admin`, `normal` y `viewer`, y sus usuarios a
partir de las variables de entorno. Para producción, usa HTTPS, `DEBUG=False` y
un `ALLOWED_HOSTS` limitado a los dominios del despliegue.

## Configuración de DRF

DRF usa JWT en la cabecera `Authorization: Bearer ...`; a diferencia de una
sesión de navegador, cada petición de API incluye su credencial y los access
tokens expiran a los 10 minutos. Los refresh tokens duran un día, se rotan y
los anteriores se invalidan para reducir el impacto de una filtración.

La API solo renderiza JSON y exige autenticación por defecto. La paginación
limita las respuestas a 10 reservas por página; `search` permite filtrar por
nombre o estado y `ordering` ordenar por fecha, nombre, horas o estado.

## Autenticación y permisos

Solicita un par de tokens con las credenciales creadas por `setup_roles`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/token/ `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"USUARIO\",\"password\":\"CONTRASENA\"}"
```

Usa el `access` recibido en la cabecera `Authorization: Bearer ACCESS_TOKEN`.
Renueva el access token mediante `POST /api/token/refresh/`, enviando el
`refresh` en el cuerpo JSON. No pongas tokens en URLs, código, capturas ni
archivos versionados.

- Cualquier usuario autenticado puede listar y consultar reservas.
- Los grupos `normal` y `admin` pueden crear reservas.
- Solo `admin` o personal marcado como `is_staff` puede editar o eliminar.
- El grupo `viewer` solo consulta.
- La eliminación es lógica: responde `204` y conserva el registro histórico.

## Endpoints

| Método | Endpoint | Acceso | Resultado |
|---|---|---|---|
| `POST` | `/api/token/` | Público | Obtiene access y refresh JWT |
| `POST` | `/api/token/refresh/` | Público con refresh JWT | Rota y renueva los tokens |
| `GET` | `/api/reservas/` | Autenticado | Lista reservas paginadas |
| `POST` | `/api/reservas/` | `normal`, `admin` | Crea una reserva |
| `GET` | `/api/reservas/{id}/` | Autenticado | Consulta una reserva |
| `PUT`, `PATCH` | `/api/reservas/{id}/` | `admin` | Actualiza y recalcula el resultado |
| `DELETE` | `/api/reservas/{id}/` | `admin` | Elimina lógicamente |
| `GET` | `/api/schema/` | Público | Esquema OpenAPI JSON |
| `GET` | `/api/docs/` | Público | Documentación Swagger |

`id`, `estado`, `motivo` y `fecha` son de solo lectura. El servidor calcula el
estado y el motivo mediante la regla de negocio compartida con el CRUD HTML.
Las horas no positivas conservan el comportamiento ES2: la regla crea el
registro con estado `Dato inválido`; errores de formato, campos faltantes o un
nombre vacío responden `400`.

Las respuestas usan los códigos HTTP de DRF: `200` al consultar/actualizar,
`201` al crear, `204` al eliminar, `400` ante validación inválida, `401` sin
autenticación, `403` sin permiso y `404` para un id inexistente. Los errores
de validación identifican el campo que debe corregirse.

## Pruebas

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test core
```

Las pruebas de `core` cubren el CRUD HTML existente y la API: JWT y refresco,
roles, JSON, validación, reglas de negocio, borrado lógico, paginación,
búsqueda, `404` y esquema OpenAPI.

Al preparar la entrega, excluye `.env`, `env/`, `db.sqlite3`, `.git/` y
`__pycache__/`. El `.gitignore` ya contiene las exclusiones locales principales.
