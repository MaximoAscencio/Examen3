"""
Librería de ordenamientos EXTERNOS (los datos viven en archivos de texto).

Los algoritmos son los del equipo (carpeta ADA3 - MetOrdenaExt/):
    - Intercalación de dos archivos ordenados
    - Mezcla directa
    - Mezcla equilibrada natural
Aquí se reúnen con una interfaz común y se les agregó el orden descendente.

Los archivos son TXT con un número entero por línea. Durante el proceso se
crean archivos auxiliares en una carpeta temporal "_tmp_..." junto al archivo
de destino; al terminar se borran.

Uso:
    from ordenamientos_externos import ordenar_externo
    ordenar_externo("entrada.txt", "salida.txt", "mezcla_directa", ascendente=True)

Reglas del examen: no se usan los métodos de ordenamiento automáticos de Python.
Solo se usan os y open().
"""

import os
import time

# En Windows un archivo puede quedar bloqueado un instante (OneDrive, antivirus,
# el explorador de archivos). Por eso las operaciones de reemplazo y borrado se
# reintentan unas cuantas veces antes de rendirse.
INTENTOS_BLOQUEO = 10
ESPERA_BLOQUEO = 0.3       # segundos entre intentos


# ----------------------------------------------------------------------
# Utilidades de archivos
# ----------------------------------------------------------------------

def leer_numero(archivo):
    """Lee el siguiente número del archivo; None si ya no hay más."""
    linea = archivo.readline()
    return int(linea) if linea else None


def va_antes(a, b, ascendente):
    """True si 'a' puede salir antes que 'b' en el orden pedido."""
    if ascendente:
        return a <= b
    return a >= b


def mostrar_archivo(ruta, etiqueta):
    """Muestra el archivo sin cargarlo completo en memoria.
    Una línea en blanco se muestra como | (separador de tramos)."""
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


def copiar_archivo(origen, destino):
    """Copia un archivo línea por línea."""
    with open(origen, encoding="utf-8") as entrada, \
            open(destino, "w", encoding="utf-8") as salida:
        for linea in entrada:
            salida.write(linea)


def _reintentar(operacion, *argumentos):
    """Ejecuta operacion(*argumentos); si el archivo está bloqueado
    (PermissionError) espera un poco y vuelve a intentar."""
    for intento in range(INTENTOS_BLOQUEO):
        try:
            return operacion(*argumentos)
        except PermissionError:
            if intento == INTENTOS_BLOQUEO - 1:
                raise
            time.sleep(ESPERA_BLOQUEO)


def publicar_archivo(origen, destino):
    """Deja 'origen' como 'destino'. Primero intenta reemplazarlo; si Windows lo
    impide, copia el contenido y borra el origen."""
    try:
        _reintentar(os.replace, origen, destino)
    except PermissionError:
        _reintentar(copiar_archivo, origen, destino)
        try:
            _reintentar(os.remove, origen)
        except PermissionError:
            pass            # la carpeta temporal se limpia después


def _crear_carpeta_trabajo(destino, nombre):
    """Crea la carpeta de archivos auxiliares junto al destino."""
    base = os.path.dirname(os.path.abspath(destino))
    carpeta = os.path.join(base, "_tmp_" + nombre)
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def _borrar_carpeta_trabajo(carpeta):
    """Borra los archivos auxiliares y la carpeta."""
    if not os.path.isdir(carpeta):
        return
    try:
        for nombre in os.listdir(carpeta):
            _reintentar(os.remove, os.path.join(carpeta, nombre))
        _reintentar(os.rmdir, carpeta)
    except OSError:
        pass                # si no se pudo borrar, no se interrumpe el ordenamiento


# ----------------------------------------------------------------------
# Intercalación de dos archivos ya ordenados
# ----------------------------------------------------------------------

def intercalar_archivos(ruta_a, ruta_b, destino, ascendente=True):
    """Fusiona dos archivos ya ordenados en una pasada, conservando repetidos."""
    temporal = destino + ".tmp"
    with open(ruta_a, encoding="utf-8") as a, \
            open(ruta_b, encoding="utf-8") as b, \
            open(temporal, "w", encoding="utf-8") as salida:
        primero = leer_numero(a)
        segundo = leer_numero(b)
        while primero is not None and segundo is not None:
            if va_antes(primero, segundo, ascendente):
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
    # El resultado se publica al terminar para evitar archivos incompletos.
    publicar_archivo(temporal, destino)


# ----------------------------------------------------------------------
# Mezcla directa
# ----------------------------------------------------------------------

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


def fusionar_bloques(auxiliar_a, auxiliar_b, destino, longitud, ascendente=True):
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
                if disponible_a and (not disponible_b
                                     or va_antes(primero, segundo, ascendente)):
                    salida.write(f"{primero}\n")
                    primero = leer_numero(a)
                    usados_a += 1
                else:
                    salida.write(f"{segundo}\n")
                    segundo = leer_numero(b)
                    usados_b += 1


def mezcla_directa(origen, destino, ascendente=True, mostrar=False):
    """Ordena el archivo 'origen' y deja el resultado en 'destino'.
    Regresa el número de pasadas (fusiones) realizadas."""
    carpeta = _crear_carpeta_trabajo(destino, "mezcla_directa")
    trabajo = os.path.join(carpeta, "F.txt")
    auxiliar_a = os.path.join(carpeta, "F1.txt")
    auxiliar_b = os.path.join(carpeta, "F2.txt")
    pasada = 0
    try:
        copiar_archivo(origen, trabajo)
        longitud = 1
        while True:
            cantidad = repartir_bloques(trabajo, auxiliar_a, auxiliar_b, longitud)
            if longitud >= cantidad:
                break
            fusionar_bloques(auxiliar_a, auxiliar_b, trabajo, longitud, ascendente)
            pasada += 1
            if mostrar:
                mostrar_archivo(trabajo, f"Pasada {pasada}, bloques de hasta {2 * longitud}")
            longitud *= 2
        publicar_archivo(trabajo, destino)
    finally:
        _borrar_carpeta_trabajo(carpeta)
    return pasada


# ----------------------------------------------------------------------
# Mezcla equilibrada natural
# ----------------------------------------------------------------------

def distribuir_tramos(origen, ruta_a, ruta_b, ascendente=True):
    """Detecta los tramos naturales (secuencias que ya vienen en el orden
    pedido) y los reparte de forma alternada entre dos archivos."""
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
            elif not va_antes(anterior, numero, ascendente):
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


def fusionar_tramos(ruta_a, ruta_b, ruta_c, ruta_d, ascendente=True):
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
                if primero is not None and (segundo is None
                                            or va_antes(primero, segundo, ascendente)):
                    salida.write(f"{primero}\n")
                    primero = next(tramo_a, None)
                else:
                    salida.write(f"{segundo}\n")
                    segundo = next(tramo_b, None)
            salida.write("\n")
            cantidad += 1
    return cantidad


def mezcla_equilibrada(origen, destino, ascendente=True, mostrar=False):
    """Ordena el archivo 'origen' y deja el resultado en 'destino'.
    Regresa el número de fusiones realizadas."""
    carpeta = _crear_carpeta_trabajo(destino, "mezcla_equilibrada")
    rutas = [os.path.join(carpeta, f"F{indice}.txt") for indice in range(1, 5)]
    entrada_a, entrada_b, salida_a, salida_b = rutas
    pasada = 0
    try:
        tramos = distribuir_tramos(origen, entrada_a, entrada_b, ascendente)
        if mostrar:
            print(f"Tramos naturales iniciales: {tramos}. El símbolo | separa tramos.")
            mostrar_archivo(entrada_a, "F1")
            mostrar_archivo(entrada_b, "F2")
        while tramos > 1:
            tramos = fusionar_tramos(entrada_a, entrada_b, salida_a, salida_b, ascendente)
            pasada += 1
            if mostrar:
                print(f"Fusión {pasada}, tramos restantes: {tramos}")
                mostrar_archivo(salida_a, "F" + str(rutas.index(salida_a) + 1))
                mostrar_archivo(salida_b, "F" + str(rutas.index(salida_b) + 1))
            # Las dos salidas se convierten en entradas para la siguiente pasada.
            entrada_a, entrada_b, salida_a, salida_b = (
                salida_a, salida_b, entrada_a, entrada_b
            )
        resultado = os.path.join(carpeta, "resultado.txt")
        with open(entrada_a, encoding="utf-8") as entrada, \
                open(resultado, "w", encoding="utf-8") as salida:
            for linea in entrada:
                if linea.strip():
                    salida.write(linea)
        publicar_archivo(resultado, destino)
    finally:
        _borrar_carpeta_trabajo(carpeta)
    return pasada


# ----------------------------------------------------------------------
# Interfaz común
# ----------------------------------------------------------------------

# clave -> (nombre para mostrar, función)
ALGORITMOS = {
    "mezcla_directa": ("Mezcla directa", mezcla_directa),
    "mezcla_equilibrada": ("Mezcla equilibrada natural", mezcla_equilibrada),
}

CLAVES = ["mezcla_directa", "mezcla_equilibrada"]


def ordenar_externo(origen, destino, algoritmo, ascendente=True, mostrar=False):
    """Ordena el archivo TXT 'origen' y escribe el resultado en 'destino'.
    Regresa el número de pasadas realizadas."""
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo externo desconocido: {algoritmo}")
    funcion = ALGORITMOS[algoritmo][1]
    return funcion(origen, destino, ascendente=ascendente, mostrar=mostrar)
