# Uso de herramienta de IA

Consulté a una herramienta de IA para ordenar el plan del proyecto según la estructura solicitada: problema, solución, alcance, prioridades MoSCoW, datos de entrada, regla de decisión y pantalla Django.

La consulta fue: "Ayúdame a crear un plan para un sistema de reservas de canchas deportivas que pida nombre y horas, use 3 canchas, permita hasta 2 horas, tenga cuatro resultados, guarde en JSON y muestre los registros con Django. No uses base de datos, login ni API."

La primera propuesta incluía mostrar las canchas disponibles como función principal y sugería agregar cuentas de usuario. Eso no correspondía al MVP ni al alcance de esta evaluación, así que lo corregí: dejé como Must solo pedir datos, decidir, guardar en JSON y mostrar en Django. También definí que las solicitudes rechazadas se guardan, pero solo las aceptadas ocupan una cancha.
