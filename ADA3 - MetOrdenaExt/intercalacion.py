from pathlib import Path
from tempfile import TemporaryDirectory
import os


def leer_numero(archivo):
    linea = archivo.readline()
    return int(linea) if linea else None


def intercalar_archivos(ruta_a, ruta_b, destino):
    """Fusiona dos archivos ordenados en una pasada, conservando repetidos."""
    destino = Path(destino)
    # La salida se publica al terminar para evitar resultados incompletos.
    with TemporaryDirectory(dir=destino.parent) as carpeta:
        temporal = Path(carpeta) / "resultado.txt"
        with open(ruta_a, encoding="utf-8") as a, \
                open(ruta_b, encoding="utf-8") as b, \
                open(temporal, "w", encoding="utf-8") as salida:
            primero = leer_numero(a)
            segundo = leer_numero(b)
            while primero is not None and segundo is not None:
                if primero <= segundo:
                    salida.write(f"{primero}\n")
                    primero = leer_numero(a)
                else:
                    salida.write(f"{segundo}\n")
                    segundo = leer_numero(b)
            while primero is not None:
                salida.write(f"{primero}\n")
                primero = leer_numero(a)
            while segundo is not None:
                salida.write(f"{segundo}\n")
                segundo = leer_numero(b)
        os.replace(temporal, destino)


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
    carpeta = Path(__file__).resolve().parent / "datos_intercalacion"
    carpeta.mkdir(exist_ok=True)
    ruta_a = carpeta / "sucursal_a.txt"
    ruta_b = carpeta / "sucursal_b.txt"
    destino = carpeta / "resultado_intercalacion.txt"
    while True:
        print("\nINTERCALACIÓN — CÓDIGOS DE DOS SUCURSALES")
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
                escribir_ejemplo(ruta_a, [101, 108, 125, 140])
                escribir_ejemplo(ruta_b, [103, 108, 119, 132, 150])
            else:
                print("Cada sucursal debe ingresar sus números de menor a mayor.")
                capturar_archivo(ruta_a, "sucursal A", ordenado=True)
                capturar_archivo(ruta_b, "sucursal B", ordenado=True)
            mostrar_archivo(ruta_a, "Sucursal A")
            mostrar_archivo(ruta_b, "Sucursal B")
            intercalar_archivos(ruta_a, ruta_b, destino)
            mostrar_archivo(destino, "Resultado")
            print(f"Archivo guardado en {destino}")
        except OSError as error:
            print(f"No se pudo completar el manejo de archivos: {error}")


if __name__ == "__main__":
    main()
