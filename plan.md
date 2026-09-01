# Plan: reservas de canchas deportivas

## Apartado de negocio

**Problema:** En un recinto deportivo, el control manual dificulta saber cuantas canchas quedan disponibles y controlar que una solicitud no supere el tiempo maximo. Esto puede provocar errores al organizar las reservas.

**Solucion:** El programa recibe el nombre de una persona y las horas solicitadas. Valida la solicitud, informa el resultado con su motivo y guarda cada registro para consultarlo en una pagina web.

**Alcance:** Esta version registra solicitudes de una en una, trabaja con 3 canchas y permite reservar hasta 2 horas. No incluye cuentas, cancelaciones, modificaciones ni base de datos.

**MoSCoW:**

- **Must:** pedir nombre y horas; validar y decidir; guardar en JSON; mostrar registros en Django.
- **Should:** modificar una reserva; mostrar canchas disponibles.
- **Could:** cancelar una reserva; ordenar por nombre.
- **Won't:** crear cuentas de usuario y contrasenas.

## Apartado tecnico

**Datos de entrada:** `nombre` es texto (`str`) y `horas` es un numero entero (`int`) convertido desde `input()`. Las canchas disponibles se calculan restando las reservas aceptadas a las 3 canchas iniciales.

**Regla de decision:** Si las horas son menores o iguales a cero, el dato es invalido. Si son mayores a 2, se rechaza por superar el maximo. Si no quedan canchas, se rechaza por falta de disponibilidad. En cualquier otro caso, se acepta.

**Paquete externo:** Se usa `tabulate` para mostrar los registros alineados en una tabla en la consola. `json` es parte de Python y se usa para guardar los datos.

**Pantalla web:** La direccion `/` muestra un formulario para ingresar una solicitud y una tabla con todos los registros guardados en `datos.json`.
