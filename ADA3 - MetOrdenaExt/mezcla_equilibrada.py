from pathlib import Path
from tempfile import TemporaryDirectory
import os


def distribuir_tramos(origen, ruta_a, ruta_b):
    """Detecta los tramos naturales por descensos y los reparte alternadamente."""
    tramos = 0
    anterior = None
    with open(origen, encoding="utf-8") as entrada, \
            open(ruta_a, "w", encoding="utf-8") as a, \
            open(ruta_b, "w", encoding="utf-8") as b:
        salidas = (a, b)
        indice = 0
        for linea in entrada:
            numero = int(linea)
            if anterior is None:
                tramos = 1
            elif numero < anterior:
                salidas[indice].write("\n")
                indice = 1 - indice
                tramos += 1
            salidas[indice].write(f"{numero}\n")
            anterior = numero
        if tramos:
            salidas[indice].write("\n")
    return tramos


def leer_tramo(archivo):
    """Entrega un tramo registro por registro y consume su separador."""
    linea = archivo.readline()
    while linea and linea.strip():
        yield int(linea)
        linea = archivo.readline()


def fusionar_tramos(ruta_a, ruta_b, ruta_c, ruta_d):
    """Fusiona parejas de tramos y alterna su escritura en las salidas."""
    cantidad = 0
    with open(ruta_a, encoding="utf-8") as a, \
            open(ruta_b, encoding="utf-8") as b, \
            open(ruta_c, "w", encoding="utf-8") as c, \
            open(ruta_d, "w", encoding="utf-8") as d:
        salidas = (c, d)
        while True:
            tramo_a = leer_tramo(a)
            tramo_b = leer_tramo(b)
            primero = next(tramo_a, None)
            segundo = next(tramo_b, None)
            if primero is None and segundo is None:
                break
            salida = salidas[cantidad % 2]
            while primero is not None or segundo is not None:
                if primero is not None and (segundo is None or primero <= segundo):
                    salida.write(f"{primero}\n")
                    primero = next(tramo_a, None)
                else:
                    salida.write(f"{segundo}\n")
                    segundo = next(tramo_b, None)
            salida.write("\n")
            cantidad += 1
    return cantidad


def mezcla_equilibrada(origen, destino, mostrar=True):
    destino = Path(destino)
    with TemporaryDirectory(dir=destino.parent) as carpeta:
        carpeta = Path(carpeta)
        rutas = [carpeta / f"F{indice}.txt" for indice in range(1, 5)]
        entrada_a, entrada_b, salida_a, salida_b = rutas
        tramos = distribuir_tramos(origen, entrada_a, entrada_b)
        if mostrar:
            print(f"Tramos naturales iniciales: {tramos}. El símbolo | separa tramos.")
            mostrar_archivo(entrada_a, "F1")
            mostrar_archivo(entrada_b, "F2")
        pasada = 0
        while tramos > 1:
            tramos = fusionar_tramos(entrada_a, entrada_b, salida_a, salida_b)
            pasada += 1
            if mostrar:
                print(f"Fusión {pasada}, tramos restantes: {tramos}")
                mostrar_archivo(salida_a, salida_a.stem)
                mostrar_archivo(salida_b, salida_b.stem)
            # Las dos salidas se convierten en entradas para la siguiente pasada.
            entrada_a, entrada_b, salida_a, salida_b = (
                salida_a, salida_b, entrada_a, entrada_b
            )
        resultado = carpeta / "resultado.txt"
        with open(entrada_a, encoding="utf-8") as entrada, \
                open(resultado, "w", encoding="utf-8") as salida:
            for linea in entrada:
                if linea.strip():
                    salida.write(linea)
        os.replace(resultado, destino)
    return pasada


def leer_entero(mensaje, minimo=None):
    while True:
        try:
            numero = int(input(mensaje))
            if minimo is not None and numero < minimo:
                print(f"El valor debe ser mayor o igual que {minimo}.")
                continue
            return numero
        except ValueError:
            print("Escribe un número entero válido.")


def mostrar_archivo(ruta, etiqueta):
    """Muestra el archivo sin cargarlo completo en memoria."""
    print(f"{etiqueta}: [", end="")
    separador = ""
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            if linea.strip():
                print(separador + linea.strip(), end="")
                separador = ", "
            else:
                separador = " | "
    print("]")


def capturar_archivo(ruta, etiqueta, ordenado=False):
    print(f"\nCaptura de {etiqueta}")
    cantidad = leer_entero("Cantidad de números (puede ser 0): ", minimo=0)
    anterior = None
    with open(ruta, "w", encoding="utf-8") as archivo:
        for indice in range(cantidad):
            numero = leer_entero(f"Número {indice + 1}: ")
            while ordenado and anterior is not None and numero < anterior:
                print(f"La entrada debe estar ordenada. Ingresa un valor >= {anterior}.")
                numero = leer_entero(f"Número {indice + 1}: ")
            archivo.write(f"{numero}\n")
            anterior = numero


def escribir_ejemplo(ruta, numeros):
    with open(ruta, "w", encoding="utf-8") as archivo:
        for numero in numeros:
            archivo.write(f"{numero}\n")


def main():
    carpeta = Path(__file__).resolve().parent / "datos_mezcla_equilibrada"
    carpeta.mkdir(exist_ok=True)
    origen = carpeta / "registros.txt"
    destino = carpeta / "resultado_mezcla_equilibrada.txt"
    while True:
        print("\nMEZCLA EQUILIBRADA NATURAL — REGISTROS DE ENTREGAS")
        print("1. Ejecutar ejemplo\n2. Capturar números\n3. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "3":
            print("Programa finalizado.")
            break
        if opcion not in ("1", "2"):
            print("Elige 1, 2 o 3.")
            continue
        try:
            if opcion == "1":
                escribir_ejemplo(origen, [12, 18, 25, 4, 9, 30, 7, 14, 22, 3, 11])
            else:
                capturar_archivo(origen, "registros de entregas")
            mostrar_archivo(origen, "Original")
            pasadas = mezcla_equilibrada(origen, destino)
            mostrar_archivo(destino, "Resultado")
            print(f"Fusiones realizadas: {pasadas}")
            print(f"Archivo guardado en {destino}")
        except OSError as error:
            print(f"No se pudo completar el manejo de archivos: {error}")


if __name__ == "__main__":
    main()
