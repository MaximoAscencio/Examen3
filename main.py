"""
Sistema de Procesamiento y Ordenamiento Masivo de Datos
Examen parcial - Algoritmos de ordenamiento y búsqueda

Interfaz de CONSOLA. Solo se encarga de pedir datos y mostrar resultados;
toda la lógica está en backend.py, que usa las librerías del equipo:
    archivos.py               -> lectura/escritura de TXT y XLSX
    ordenamientos_internos.py -> burbuja, selección, inserción, shell, quick, heap, radix
    ordenamientos_externos.py -> mezcla directa, mezcla equilibrada natural
    busquedas.py              -> secuencial, binaria, hash

Ejecutar:  python main.py
"""

import os

import backend
from backend import formato_tiempo, texto_orden


# ----------------------------------------------------------------------
# Entrada de datos del usuario
# ----------------------------------------------------------------------

def pedir_entero(mensaje, minimo=None, maximo=None):
    while True:
        texto = input(mensaje).strip()
        try:
            numero = int(texto)
        except ValueError:
            print("  Escribe un número entero válido.")
            continue
        if minimo is not None and numero < minimo:
            print(f"  El valor debe ser mayor o igual que {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"  El valor debe ser menor o igual que {maximo}.")
            continue
        return numero


def elegir_opcion(titulo, opciones):
    """Muestra una lista numerada y regresa el índice elegido (0, 1, ...)."""
    print(titulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    return pedir_entero("Opción: ", 1, len(opciones)) - 1


# ----------------------------------------------------------------------
# A) Cargar archivo
# ----------------------------------------------------------------------

def cargar(sesion):
    print("\n--- CARGAR ARCHIVO (TXT o XLSX) ---")
    disponibles = backend.listar_archivos_datos()
    ruta = None
    if disponibles:
        print("Archivos en la carpeta datos/:")
        for i in range(len(disponibles)):
            print(f"  {i + 1}. {disponibles[i]}")
        print("  0. Escribir otra ruta")
        eleccion = pedir_entero("Opción: ", 0, len(disponibles))
        if eleccion > 0:
            ruta = os.path.join(backend.CARPETA_DATOS, disponibles[eleccion - 1])
    if ruta is None:
        ruta = input("Ruta del archivo .txt o .xlsx: ").strip().strip('"')

    try:
        invalidas = sesion.cargar(ruta)
    except (OSError, ValueError) as error:
        print(f"\nNo se pudo cargar el archivo: {error}")
        return

    print(f"\nArchivo cargado: {sesion.nombre_archivo}")
    print(f"Registros leídos: {sesion.total}")
    if invalidas:
        print(f"Líneas/celdas ignoradas por no ser enteros: {invalidas}")


# ----------------------------------------------------------------------
# B) Ordenar datos
# ----------------------------------------------------------------------

def ordenar(sesion):
    if not sesion.cargado:
        print("\nPrimero carga un archivo con datos (opción 1).")
        return
    print("\n--- ORDENAR DATOS ---")
    tipo_idx = elegir_opcion("Tipo de ordenamiento:",
                             [nombre for _, nombre in backend.TIPOS_ORDENAMIENTO])
    tipo = backend.TIPOS_ORDENAMIENTO[tipo_idx][0]

    lista = backend.algoritmos(tipo)
    idx = elegir_opcion("\nAlgoritmo:", [nombre for _, nombre in lista])
    clave, nombre = lista[idx]

    orden_idx = elegir_opcion("\nOrden:", ["Ascendente (menor a mayor)",
                                           "Descendente (mayor a menor)"])
    ascendente = orden_idx == 0

    print(f"\nOrdenando {sesion.total} registros con {nombre} ({texto_orden(ascendente)})...")
    try:
        r = sesion.ordenar(tipo, clave, ascendente)
    except (OSError, ValueError) as error:
        print(f"\nNo se pudo ordenar: {error}")
        return

    print("Listo.")
    print(f"Tiempo de ejecución: {formato_tiempo(r['segundos'])}")
    if r["pasadas"] is not None:
        print(f"Pasadas de mezcla: {r['pasadas']}")
    if tipo == "externo":
        print("Archivos usados: resultados/entrada_externa.txt -> resultados/salida_externa.txt")
    if not r["correcto"]:
        print("AVISO: la verificación indica que el resultado NO quedó ordenado.")


# ----------------------------------------------------------------------
# C) Buscar un valor
# ----------------------------------------------------------------------

def buscar(sesion):
    if not sesion.cargado:
        print("\nPrimero carga un archivo con datos (opción 1).")
        return
    print("\n--- BUSCAR UN VALOR ---")
    idx = elegir_opcion("Método de búsqueda:",
                        [nombre for _, nombre in backend.METODOS_BUSQUEDA])
    metodo, nombre = backend.METODOS_BUSQUEDA[idx]
    valor = pedir_entero("Valor a buscar: ")

    try:
        r = sesion.buscar(metodo, valor)
    except ValueError as error:
        print(f"\n{error}")
        return

    if r["segundos_construccion"] is not None:
        print(f"Tabla hash construida en {formato_tiempo(r['segundos_construccion'])} "
              f"(tamaño {sesion.tabla_hash.tamanio}).")
    nombre_corto = nombre.split(" (")[0]
    if r["posicion"] == -1:
        print(f"\nBúsqueda {nombre_corto}: el valor {valor} NO se encontró.")
    else:
        print(f"\nBúsqueda {nombre_corto}: el valor {valor} se encontró en la posición "
              f"{r['posicion'] + 1} (la primera es la 1).")
        if r["repeticiones"]:
            print(f"El valor aparece {r['repeticiones']} vez/veces en los datos.")
    print(f"Tiempo de búsqueda: {formato_tiempo(r['segundos'])}")


# ----------------------------------------------------------------------
# D) Mostrar resultados
# ----------------------------------------------------------------------

def mostrar(sesion):
    if not sesion.cargado:
        print("\nPrimero carga un archivo con datos (opción 1).")
        return
    print("\n--- RESULTADOS ---")
    if sesion.ordenado:
        u = sesion.ultimo
        print(f"Datos ordenados con {u['algoritmo']} ({texto_orden(u['ascendente'])}).")
    else:
        print("Los datos están tal como se cargaron (sin ordenar).")
    print(f"Primeros 20 elementos: {sesion.primeros(20)}")
    print(f"Últimos 20 elementos:  {sesion.ultimos(20)}")
    print(f"Total de registros: {sesion.total}")
    if sesion.ordenado:
        print(f"Tiempo del último ordenamiento: {formato_tiempo(sesion.ultimo['segundos'])}")


# ----------------------------------------------------------------------
# E) Exportar resultados
# ----------------------------------------------------------------------

def exportar(sesion):
    if not sesion.cargado:
        print("\nPrimero carga un archivo con datos (opción 1).")
        return
    print("\n--- EXPORTAR RESULTADOS ---")
    if not sesion.ordenado:
        print("AVISO: aún no ordenas los datos; se exportarán tal como se cargaron.")
    idx = elegir_opcion("Formato del archivo de salida:",
                        [nombre for _, nombre in backend.FORMATOS_SALIDA])
    formato = backend.FORMATOS_SALIDA[idx][0]

    sugerido = "datos_ordenados"
    nombre = input(f"Nombre del archivo sin extensión (Enter = {sugerido}): ").strip()
    if not nombre:
        nombre = sugerido

    try:
        ruta_datos, ruta_reporte = sesion.exportar(formato, nombre)
    except (OSError, ValueError) as error:
        print(f"\nNo se pudo exportar: {error}")
        return
    print("\nArchivos guardados:")
    print(f"  {ruta_datos}")
    print(f"  {ruta_reporte}")


# ----------------------------------------------------------------------
# Extra) Comparar algoritmos
# ----------------------------------------------------------------------

def comparar(sesion):
    if not sesion.cargado:
        print("\nPrimero carga un archivo con datos (opción 1).")
        return
    print(f"\n--- COMPARACIÓN DE ALGORITMOS ({len(sesion.original)} registros, ascendente) ---")
    print("Cada algoritmo parte de los datos originales cargados.\n")
    try:
        r = sesion.comparar()
    except (OSError, ValueError) as error:
        print(f"No se pudo comparar: {error}")
        return
    for linea in r["lineas"]:
        print(linea)
    print(f"\nTabla guardada en {r['ruta']}")


# ----------------------------------------------------------------------
# Menú principal
# ----------------------------------------------------------------------

def mostrar_menu(sesion):
    print("\n==================================================")
    print(" SISTEMA DE PROCESAMIENTO Y ORDENAMIENTO MASIVO DE DATOS")
    print("==================================================")
    if sesion.cargado:
        situacion = "ordenados" if sesion.ordenado else "sin ordenar"
        print(f" Archivo: {sesion.nombre_archivo} | {sesion.total} registros | {situacion}")
    else:
        print(" Ningún archivo cargado")
    print("--------------------------------------------------")
    print(" 1. Cargar archivo (TXT o XLSX)")
    print(" 2. Ordenar datos")
    print(" 3. Buscar un valor")
    print(" 4. Mostrar resultados")
    print(" 5. Exportar resultados")
    print(" 6. Comparar algoritmos")
    print(" 0. Salir")


def main():
    sesion = backend.Sesion()
    acciones = {
        1: cargar,
        2: ordenar,
        3: buscar,
        4: mostrar,
        5: exportar,
        6: comparar,
    }
    while True:
        mostrar_menu(sesion)
        opcion = pedir_entero("Elige una opción: ", 0, 6)
        if opcion == 0:
            print("Programa finalizado.")
            break
        acciones[opcion](sesion)


if __name__ == "__main__":
    main()
