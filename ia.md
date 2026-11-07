# Uso crítico de una herramienta de IA

Se utilizó el asistente de IA integrado en VS Code como apoyo para revisar el
proyecto contra las instrucciones de Eva2. Las respuestas se contrastaron con el
código, las pruebas automatizadas y la ejecución de Django; no se aceptaron como
correctas sin verificación.

## Consulta 1: modelo, migraciones y regla de negocio

**Pregunta:** “como deberia conectar el modelo de reservas a SQLite y evitar que
la validacion de la reserva quede duplicada al crear y editar?”

**Orientación de la IA:** mantener el modelo persistido por el ORM, verificar las
migraciones y llamar a la función de decisión existente en ambas operaciones.

**Revisión y decisión:** confirmé que SQLite era el motor solicitado y que
`decidir_reserva()` ya era la fuente correcta de las reglas. Conservé esa función
sin copiarla y centralicé el guardado en `_guardar_reserva`. Verifiqué el resultado
de edición con una reserva que pasa de 1 a 3 horas y con las pruebas automatizadas.

## Consulta 2: usuarios, roles y contraseñas

**Pregunta:** “como compruebo que los roles realmente protegen las vistas y
configurar sus usuarios sin incluir contraseñas en el codigo ni en la entrega?”

**Orientación de la IA:** autorizar en las vistas del servidor, probar las URL
directas con cada rol, usar las contraseñas del entorno con los validadores de
Django y excluir los archivos locales sensibles del paquete de entrega.

**Revisión y decisión:** al revisar la configuración detecté valores de ejemplo
predecibles en la plantilla del entorno y una carpeta local llamada `env/` que no
estaba cubierta por `.gitignore`. Reemplacé esos valores por campos vacíos,
amplié las exclusiones y documenté que el `.env`, el entorno virtual y la base de
datos local no se deben incluir en el ZIP. Verifiqué los permisos con pruebas de
acceso directo y la configuración de contraseñas con `setup_roles`.

## Consulta 3: formularios y administrador

**Pregunta:** “que validaciones y controles conviene revisar en los formularios
del crud y en django admin sin alterar la regla del ejercicio anterior?”

**Orientación de la IA:** validar entradas también en el servidor, personalizar el
admin y retirar plantillas antiguas que no formen parte de la aplicación.

**Revisión y decisión:** añadí `min=1` como ayuda del formulario, manteniendo la
validación de servidor y el resultado de `decidir_reserva()` para valores no
positivos. Eliminé `resumen.html` al confirmar que ninguna ruta lo utiliza; añadí
validación del nombre en el admin y conservé columnas, filtros y búsqueda.

## Evidencia y límites

Las decisiones se comprobaron con `manage.py check`, la verificación de
migraciones y las pruebas de `core`. La herramienta ayudó a identificar cambios
posibles; la selección final se basó en los requerimientos de Eva2 y en los
resultados observables del proyecto.

## Evaluación ES3: API, autenticación y permisos

**Consulta:** “A partir de las instrucciones y la rúbrica ES3, completa la API
sin quitar el CRUD HTML, aplica seguridad y dime qué dependencias faltan.”

**Recomendación generada para este proyecto:** usar DRF con un serializer de
campos permitidos explícitamente, JWT con expiración y rotación de refresh,
permisos por rol, paginación, documentación OpenAPI y pruebas HTTP. Reutilizar
la decisión de negocio y el borrado lógico existentes en vez de duplicarlos.

**Qué adopté y por qué:** adopté JWT porque la pauta valora expiración o
refresco; el access token dura 10 minutos, el refresh dura un día y la rotación
invalida el refresh anterior. Los endpoints de reservas requieren autenticación:
`viewer` consulta, `normal` y `admin` crean, y solo `admin`/`is_staff` modifica
o elimina. El serializer limita los campos y deja `estado`, `motivo` y `fecha`
como solo lectura. Paginación de 10, búsqueda, orden y esquema OpenAPI completan
la configuración, y los tests comprueban sus respuestas.

**Qué descarté y qué estaba mal:** no habilité `AllowAny` en las reservas para
facilitar pruebas ni di permisos de escritura a cualquier usuario autenticado;
eso abriría datos u operaciones a roles que en ES2 son de solo lectura. Aclaro
que `AllowAny` fue una alternativa de seguridad evaluada, no una recomendación
que esta conversación haya atribuido a la herramienta. También descarté hacer
editable el estado porque permitiría al cliente saltarse la regla de decisión.

**Verificación y decisión propia:** mantuve el comportamiento de ES2 para horas
no positivas: la regla las registra como `Dato inválido`, en lugar de cambiar
silenciosamente esa lógica a un error HTTP. La API devuelve `400` para errores
de formato/campos y `201` cuando la regla procesa la solicitud, incluso si su
estado de negocio es inválido. Añadí pruebas para ambos casos, roles, rotación
JWT, paginación, borrado lógico, `404` y esquema. La recomendación de IA no se
consideró evidencia por sí sola; se contrastó con la implementación y las
pruebas.
