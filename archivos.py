"""
Manejo de archivos TXT y XLSX.

TXT : un número entero por línea.
XLSX: números enteros en la columna A de la primera hoja (la primera fila
      puede ser un encabezado de texto, por ejemplo "Numero").

Solo se usan os, open() y openpyxl (permitidos por el examen).
"""

import os

from openpyxl import Workbook, load_workbook


def extension(ruta):
    """Extensión en minúsculas, por ejemplo '.txt'."""
    return os.path.splitext(ruta)[1].lower()


# ----------------------------------------------------------------------
# Lectura
# ----------------------------------------------------------------------

def leer_txt(ruta):
    """Regresa (lista de enteros, cantidad de líneas inválidas)."""
    datos = []
    invalidas = 0
    with open(ruta, encoding="utf-8-sig") as archivo:
        for linea in archivo:
            texto = linea.strip()
            if not texto:
                continue
            try:
                datos.append(int(texto))
            except ValueError:
                invalidas += 1
    return datos, invalidas


def leer_xlsx(ruta):
    """Regresa (lista de enteros, cantidad de celdas inválidas)."""
    datos = []
    invalidas = 0
    libro = load_workbook(ruta, read_only=True, data_only=True)
    try:
        hoja = libro.active
        primera = True
        for fila in hoja.iter_rows(values_only=True):
            valor = fila[0] if fila else None
            es_primera = primera
            primera = False
            if valor is None:
                continue
            if isinstance(valor, bool):
                invalidas += 1
            elif isinstance(valor, int):
                datos.append(valor)
            elif isinstance(valor, float) and valor.is_integer():
                datos.append(int(valor))
            elif isinstance(valor, str):
                try:
                    datos.append(int(valor.strip()))
                except ValueError:
                    if not es_primera:           # el encabezado no cuenta como error
                        invalidas += 1
            else:
                invalidas += 1
    finally:
        libro.close()
    return datos, invalidas


def cargar_archivo(ruta):
    """Lee un TXT o XLSX según su extensión. Regresa (datos, inválidas)."""
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    ext = extension(ruta)
    if ext == ".txt":
        return leer_txt(ruta)
    if ext == ".xlsx":
        return leer_xlsx(ruta)
    raise ValueError("Formato no permitido: usa un archivo .txt o .xlsx")


# ----------------------------------------------------------------------
# Escritura
# ----------------------------------------------------------------------

def escribir_txt(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as archivo:
        for numero in datos:
            archivo.write(f"{numero}\n")


def escribir_xlsx(ruta, datos):
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Datos"
    hoja.append(["Numero"])
    for numero in datos:
        hoja.append([numero])
    libro.save(ruta)


def guardar_datos(ruta, datos):
    """Guarda los datos en TXT o XLSX según la extensión de la ruta."""
    ext = extension(ruta)
    if ext == ".txt":
        escribir_txt(ruta, datos)
    elif ext == ".xlsx":
        escribir_xlsx(ruta, datos)
    else:
        raise ValueError("Formato no permitido: usa .txt o .xlsx")


def escribir_reporte(ruta, lineas):
    with open(ruta, "w", encoding="utf-8") as archivo:
        for linea in lineas:
            archivo.write(linea + "\n")
