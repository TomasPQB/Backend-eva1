# Uso crítico de una herramienta de IA

**Herramienta:** asistente de IA integrado en el entorno de desarrollo.

**Consulta textual:** “puedes cambiar cosas para mejorarlo y poder cumplir todo?”
La consulta se hizo considerando la pauta de evaluación y las instrucciones adjuntas
de la actividad.

**Orientaciones de la revisión y decisiones aplicadas:**

- Se mantuvo SQLite, que es el motor solicitado, y se verificaron las migraciones.
- Se conservó la regla `decidir_reserva()` existente y se centralizó su uso para
  que creación y edición no produzcan resultados distintos.
- Se eliminó el uso de contraseñas predeterminadas: las credenciales se configuran
  fuera del repositorio; el comando valida las contraseñas con Django y no imprime
  sus valores.
- Se protegieron las operaciones en las vistas del servidor, además de ocultar
  botones por rol en las plantillas. El cierre de sesión requiere POST con CSRF.
- Se añadió validación de formularios y del administrador; también se protegió y
  probó el acceso por URL directa. Los resultados se contrastan con migraciones
  y pruebas automatizadas descritas en `plan.md`.

La IA se usó como apoyo y revisión, no como sustituto de las pruebas ni de la
validación de los requisitos. Las decisiones finales priorizan la pauta y conservan
la estructura y la regla de negocio del proyecto.
