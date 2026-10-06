import json
from pathlib import Path
from tabulate import tabulate

TOTAL_CANCHAS = 3
MAXIMO_HORAS = 2
ARCHIVO_DATOS = Path(__file__).resolve().parent / "datos.json"


def cargar_registros():
    if not ARCHIVO_DATOS.exists():
        return []
    with ARCHIVO_DATOS.open(encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_registros(registros):
    with ARCHIVO_DATOS.open("w", encoding="utf-8") as archivo:
        json.dump(registros, archivo, indent=2, ensure_ascii=False)


def decidir_reserva(nombre, horas, canchas_disponibles):
    if horas <= 0:
        return "Dato inválido", "La cantidad de horas debe ser mayor que cero."
    if horas > MAXIMO_HORAS:
        return "Reserva rechazada", "Supera el máximo permitido de dos horas."
    if canchas_disponibles <= 0:
        return "Reserva rechazada", "No quedan canchas disponibles."
    if horas > 0 and horas <= MAXIMO_HORAS and canchas_disponibles > 0:
        return "Reserva aceptada", "La solicitud cumple las condiciones."
    return "Reserva rechazada", "La solicitud no cumple las condiciones."


def registrar_reserva(nombre, horas):
    registros = cargar_registros()
    reservas_aceptadas = sum(
        registro["estado"] == "Reserva aceptada" for registro in registros
    )
    canchas_disponibles = TOTAL_CANCHAS - reservas_aceptadas
    estado, motivo = decidir_reserva(nombre, horas, canchas_disponibles)
    registro = {
        "nombre": nombre,
        "horas": horas,
        "estado": estado,
        "motivo": motivo,
    }
    registros.append(registro)
    guardar_registros(registros)
    return registro, registros


def main():
    nombre = input("Nombre de la persona: ").strip()
    horas = int(input("Cantidad de horas: "))
    registro, registros = registrar_reserva(nombre, horas)
    print(f"{registro['estado']}: {registro['motivo']}")
    print(tabulate(registros, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    main()
