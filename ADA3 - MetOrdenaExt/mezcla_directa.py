from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil


def leer_numero(archivo):
    linea = archivo.readline()
    return int(linea) if linea else None


def repartir_bloques(origen, auxiliar_a, auxiliar_b, longitud):
    """Distribuye bloques alternos de longitud fija entre dos archivos."""
    cantidad = 0
    with open(origen, encoding="utf-8") as entrada, \
            open(auxiliar_a, "w", encoding="utf-8") as a, \
            open(auxiliar_b, "w", encoding="utf-8") as b:
        for linea in entrada:
            salida = (a, b)[(cantidad // longitud) % 2]
            salida.write(linea)
            cantidad += 1
    return cantidad


def fusionar_bloques(auxiliar_a, auxiliar_b, destino, longitud):
    """Intercala pares de bloques sin cruzar sus límites."""
    with open(auxiliar_a, encoding="utf-8") as a, \
            open(auxiliar_b, encoding="utf-8") as b, \
            open(destino, "w", encoding="utf-8") as salida:
        primero = leer_numero(a)
        segundo = leer_numero(b)
        while primero is not None or segundo is not None:
            usados_a = 0
            usados_b = 0
            while ((primero is not None and usados_a < longitud)
                   or (segundo is not None and usados_b < longitud)):
                disponible_a = primero is not None and usados_a < longitud
                disponible_b = segundo is not None and usados_b < longitud
                if disponible_a and (not disponible_b or primero <= segundo):
                    salida.write(f"{primero}\n")
                    primero = leer_numero(a)
                    usados_a += 1
                else:
                    salida.write(f"{segundo}\n")
                    segundo = leer_numero(b)
                    usados_b += 1


def mezcla_directa(origen, destino, mostrar=True):
    destino = Path(destino)
    with TemporaryDirectory(dir=destino.parent) as carpeta:
        carpeta = Path(carpeta)
        trabajo = carpeta / "F.txt"
        auxiliar_a = carpeta / "F1.txt"
        auxiliar_b = carpeta / "F2.txt"
        shutil.copyfile(origen, trabajo)
        longitud = 1
        pasada = 0
        while True:
            cantidad = repartir_bloques(trabajo, auxiliar_a, auxiliar_b, longitud)
            if longitud >= cantidad:
                break
            fusionar_bloques(auxiliar_a, auxiliar_b, trabajo, longitud)
            pasada += 1
            if mostrar:
                mostrar_archivo(trabajo, f"Pasada {pasada}, bloques de hasta {2 * longitud}")
            longitud *= 2
        os.replace(trabajo, destino)
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
    carpeta = Path(__file__).resolve().parent / "datos_mezcla_directa"
    carpeta.mkdir(exist_ok=True)
    origen = carpeta / "pedidos.txt"
    destino = carpeta / "resultado_mezcla_directa.txt"
    while True:
        print("\nMEZCLA DIRECTA — IMPORTES DE PEDIDOS EN PESOS ENTEROS")
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
                escribir_ejemplo(origen, [420, 180, 350, 120, 280, 90, 310, 200])
            else:
                capturar_archivo(origen, "importes de pedidos")
            mostrar_archivo(origen, "Original")
            pasadas = mezcla_directa(origen, destino)
            mostrar_archivo(destino, "Resultado")
            print(f"Fusiones realizadas: {pasadas}")
            print(f"Archivo guardado en {destino}")
        except OSError as error:
            print(f"No se pudo completar el manejo de archivos: {error}")


if __name__ == "__main__":
    main()
