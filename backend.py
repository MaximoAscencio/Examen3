"""
BACKEND del Sistema de Procesamiento y Ordenamiento Masivo de Datos.

Aquí vive toda la lógica del programa. No hay input() ni print(): las funciones
reciben datos y regresan resultados, y cuando algo sale mal lanzan una excepción
(ValueError, FileNotFoundError u OSError) con un mensaje en español listo para
mostrarse al usuario.

Cualquier interfaz (consola, ventana, web) solo necesita llamar a este módulo:
    - main.py        -> interfaz de consola
    - (frontend)     -> interfaz gráfica

Forma más fácil de usarlo: la clase Sesion, que recuerda el archivo cargado y
el estado de los datos.

    from backend import Sesion

    s = Sesion()
    s.cargar("datos/dataset_1000_duplicados.txt")
    r = s.ordenar("interno", "quick", ascendente=True)
    print(r["segundos"], s.primeros(), s.ultimos(), s.total)
    b = s.buscar("binaria", 4521)
    print(b["posicion"])           # -1 si no existe; empieza en 0
    s.exportar("xlsx", "mis_datos_ordenados")

Reglas del examen: no se usan los métodos de ordenamiento automáticos de Python.
"""

import os
import time

import archivos
import busquedas
import ordenamientos_externos as externos
import ordenamientos_internos as internos

BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATOS = os.path.join(BASE, "datos")
CARPETA_RESULTADOS = os.path.join(BASE, "resultados")

TIPOS_ORDENAMIENTO = [
    ("interno", "Interno (en memoria)"),
    ("externo", "Externo (con archivos auxiliares)"),
]

METODOS_BUSQUEDA = [
    ("secuencial", "Secuencial"),
    ("binaria", "Binaria (requiere datos ordenados)"),
    ("hash", "Hash"),
]

FORMATOS_SALIDA = [(".txt", "TXT"), (".xlsx", "XLSX")]


# ----------------------------------------------------------------------
# Utilidades para mostrar información
# ----------------------------------------------------------------------

def formato_tiempo(segundos):
    """Texto legible: '0.004164 s (4.164 ms)'."""
    return f"{segundos:.6f} s ({segundos * 1000:.3f} ms)"


def texto_orden(ascendente):
    return "ascendente" if ascendente else "descendente"


def algoritmos(tipo):
    """Lista de (clave, nombre) de los algoritmos de un tipo ('interno' o 'externo')."""
    modulo = _modulo(tipo)
    return [(clave, modulo.ALGORITMOS[clave][0]) for clave in modulo.CLAVES]


def listar_archivos_datos():
    """Nombres de los .txt y .xlsx que hay en la carpeta datos/."""
    if not os.path.isdir(CARPETA_DATOS):
        return []
    encontrados = []
    for nombre in os.listdir(CARPETA_DATOS):
        if archivos.extension(nombre) in (".txt", ".xlsx"):
            encontrados.append(nombre)
    return encontrados


def _modulo(tipo):
    if tipo == "interno":
        return internos
    if tipo == "externo":
        return externos
    raise ValueError("El tipo de ordenamiento debe ser 'interno' o 'externo'.")


def _asegurar_carpeta_resultados():
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)


# ----------------------------------------------------------------------
# A) Cargar archivo
# ----------------------------------------------------------------------

def cargar(ruta):
    """Lee un TXT o XLSX. Regresa (datos, cantidad_de_valores_ignorados).
    Lanza FileNotFoundError, ValueError u OSError si no se puede leer."""
    datos, invalidas = archivos.cargar_archivo(ruta)
    if not datos:
        raise ValueError("El archivo no contiene números enteros válidos.")
    return datos, invalidas


# ----------------------------------------------------------------------
# B) Ordenar datos
# ----------------------------------------------------------------------

def ordenar(original, tipo, clave, ascendente=True):
    """Ordena una copia de 'original' (la lista recibida no se modifica).

    tipo: 'interno' o 'externo'. clave: la clave del algoritmo (ver algoritmos()).
    Para los externos escribe y lee archivos TXT en resultados/; el tiempo
    medido es el del algoritmo (archivo a archivo).

    Regresa un diccionario:
        datos, segundos, pasadas (None en los internos), algoritmo (nombre),
        clave, tipo, ascendente, correcto (bool de verificación)
    """
    modulo = _modulo(tipo)
    if clave not in modulo.ALGORITMOS:
        raise ValueError(f"Algoritmo desconocido: {clave}")
    nombre = modulo.ALGORITMOS[clave][0]

    if tipo == "interno":
        inicio = time.perf_counter()
        resultado = internos.ordenar_interno(original, clave, ascendente)
        segundos = time.perf_counter() - inicio
        pasadas = None
    else:
        _asegurar_carpeta_resultados()
        entrada = os.path.join(CARPETA_RESULTADOS, "entrada_externa.txt")
        salida = os.path.join(CARPETA_RESULTADOS, "salida_externa.txt")
        archivos.escribir_txt(entrada, original)
        inicio = time.perf_counter()
        pasadas = externos.ordenar_externo(entrada, salida, clave, ascendente)
        segundos = time.perf_counter() - inicio
        resultado, _ = archivos.leer_txt(salida)

    correcto = (len(resultado) == len(original)
                and busquedas.esta_ordenada(resultado, ascendente))
    return {
        "datos": resultado,
        "segundos": segundos,
        "pasadas": pasadas,
        "algoritmo": nombre,
        "clave": clave,
        "tipo": tipo,
        "ascendente": ascendente,
        "correcto": correcto,
    }


# ----------------------------------------------------------------------
# C) Buscar un valor
# ----------------------------------------------------------------------

def sentido_de_orden(datos):
    """True si está ascendente, False si descendente, None si no está ordenada."""
    if busquedas.esta_ordenada(datos, True):
        return True
    if busquedas.esta_ordenada(datos, False):
        return False
    return None


def buscar(datos, metodo, valor, tabla_hash=None):
    """Busca 'valor' en 'datos' con 'secuencial', 'binaria' o 'hash'.

    Para reutilizar la tabla hash entre búsquedas, pásala en 'tabla_hash'
    (viene en el resultado). Regresa un diccionario:
        metodo, valor, posicion (empieza en 0; -1 si no existe), segundos,
        repeticiones (solo hash), tabla_hash, segundos_construccion
        (solo si se construyó la tabla en esta llamada)
    """
    if not datos:
        raise ValueError("No hay datos para buscar.")
    resultado = {
        "metodo": metodo,
        "valor": valor,
        "posicion": -1,
        "segundos": 0.0,
        "repeticiones": None,
        "tabla_hash": tabla_hash,
        "segundos_construccion": None,
    }

    if metodo == "secuencial":
        inicio = time.perf_counter()
        resultado["posicion"] = busquedas.busqueda_secuencial(datos, valor)
        resultado["segundos"] = time.perf_counter() - inicio

    elif metodo == "binaria":
        sentido = sentido_de_orden(datos)
        if sentido is None:
            raise ValueError("La búsqueda binaria necesita los datos ordenados. "
                             "Ordénalos primero.")
        inicio = time.perf_counter()
        resultado["posicion"] = busquedas.busqueda_binaria(datos, valor, sentido)
        resultado["segundos"] = time.perf_counter() - inicio

    elif metodo == "hash":
        if tabla_hash is None:
            inicio = time.perf_counter()
            tabla_hash = busquedas.construir_tabla_hash(datos)
            resultado["segundos_construccion"] = time.perf_counter() - inicio
            resultado["tabla_hash"] = tabla_hash
        inicio = time.perf_counter()
        posiciones = tabla_hash.buscar(valor)
        resultado["segundos"] = time.perf_counter() - inicio
        resultado["repeticiones"] = len(posiciones)
        if posiciones:
            resultado["posicion"] = posiciones[0]

    else:
        raise ValueError(f"Método de búsqueda desconocido: {metodo}")

    return resultado


# ----------------------------------------------------------------------
# E) Exportar resultados
# ----------------------------------------------------------------------

def exportar(datos, nombre_origen, formato, nombre, resumen=None):
    """Guarda los datos y un reporte en resultados/.

    formato: 'txt' o 'xlsx' (con o sin punto). nombre: sin extensión.
    resumen: el diccionario que regresa ordenar() (None si no se ordenó).
    Regresa (ruta_del_archivo_de_datos, ruta_del_reporte).
    """
    if not datos:
        raise ValueError("No hay datos para exportar.")
    ext = formato.lower()
    if not ext.startswith("."):
        ext = "." + ext
    if ext not in (".txt", ".xlsx"):
        raise ValueError("Formato no permitido: usa TXT o XLSX.")
    nombre = os.path.basename(nombre.strip()) or "datos_ordenados"

    _asegurar_carpeta_resultados()
    ruta_datos = os.path.join(CARPETA_RESULTADOS, nombre + ext)
    ruta_reporte = os.path.join(CARPETA_RESULTADOS, nombre + "_reporte.txt")

    lineas = [
        "REPORTE DE ORDENAMIENTO",
        "=======================",
        f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Archivo de origen: {nombre_origen}",
        f"Total de registros: {len(datos)}",
    ]
    if resumen:
        lineas += [
            f"Algoritmo utilizado: {resumen['algoritmo']}",
            f"Tipo: {resumen['tipo']}",
            f"Orden: {texto_orden(resumen['ascendente'])}",
            f"Tiempo de ejecución: {formato_tiempo(resumen['segundos'])}",
        ]
        if resumen["pasadas"] is not None:
            lineas.append(f"Pasadas de mezcla: {resumen['pasadas']}")
    else:
        lineas.append("Los datos no fueron ordenados.")
    lineas.append(f"Archivo ordenado: {os.path.basename(ruta_datos)}")

    archivos.guardar_datos(ruta_datos, datos)
    archivos.escribir_reporte(ruta_reporte, lineas)
    return ruta_datos, ruta_reporte


# ----------------------------------------------------------------------
# Extra) Comparar algoritmos
# ----------------------------------------------------------------------

def comparar(original, nombre_origen):
    """Ordena 'original' (ascendente) con todos los algoritmos y compara tiempos.

    Regresa un diccionario:
        filas: lista de {tipo, algoritmo, segundos, correcto}
        mas_rapido: la fila con menor tiempo
        lineas: la tabla ya formateada como lista de textos
        ruta: archivo donde se guardó la tabla
    """
    if not original:
        raise ValueError("No hay datos para comparar.")
    filas = []
    for tipo in ("interno", "externo"):
        for clave, nombre in algoritmos(tipo):
            r = ordenar(original, tipo, clave, True)
            filas.append({"tipo": tipo, "algoritmo": nombre,
                          "segundos": r["segundos"], "correcto": r["correcto"]})

    mas_rapido = filas[0]
    for fila in filas:
        if fila["segundos"] < mas_rapido["segundos"]:
            mas_rapido = fila

    lineas = [f"{'Tipo':8} {'Algoritmo':30} {'Tiempo (s)':>12}  Correcto", "-" * 62]
    for fila in filas:
        lineas.append(f"{fila['tipo']:8} {fila['algoritmo']:30} "
                      f"{fila['segundos']:12.6f}  {'sí' if fila['correcto'] else 'NO'}")
    lineas.append("-" * 62)
    lineas.append(f"Más rápido: {mas_rapido['algoritmo']} ({mas_rapido['segundos']:.6f} s)")

    _asegurar_carpeta_resultados()
    ruta = os.path.join(CARPETA_RESULTADOS, f"comparacion_{len(original)}_registros.txt")
    archivos.escribir_reporte(
        ruta, [f"Comparación con {len(original)} registros ({nombre_origen})"] + lineas)
    return {"filas": filas, "mas_rapido": mas_rapido, "lineas": lineas, "ruta": ruta}


# ----------------------------------------------------------------------
# Sesión: recuerda el estado entre una acción y otra
# ----------------------------------------------------------------------

class Sesion:
    """Guarda el archivo cargado y el estado de los datos.

    Los ordenamientos siempre parten de los datos ORIGINALES cargados, así
    que se pueden probar varios algoritmos seguidos con resultados comparables.
    """

    def __init__(self):
        self.ruta = None            # ruta del archivo cargado
        self.original = []          # datos tal como se cargaron
        self.datos = []             # datos actuales (originales u ordenados)
        self.ultimo = None          # resultado de ordenar() más reciente
        self.tabla_hash = None      # tabla hash de los datos actuales

    # --- estado -------------------------------------------------------

    @property
    def cargado(self):
        return len(self.datos) > 0

    @property
    def ordenado(self):
        return self.ultimo is not None

    @property
    def total(self):
        return len(self.datos)

    @property
    def nombre_archivo(self):
        return os.path.basename(self.ruta) if self.ruta else None

    def _exigir_datos(self):
        if not self.cargado:
            raise ValueError("Primero carga un archivo con datos.")

    # --- acciones -----------------------------------------------------

    def cargar(self, ruta):
        """Carga un archivo. Regresa cuántos valores se ignoraron.
        Si falla, la sesión anterior se conserva."""
        datos, invalidas = cargar(ruta)
        self.ruta = ruta
        self.original = datos
        self.datos = list(datos)
        self.ultimo = None
        self.tabla_hash = None
        return invalidas

    def ordenar(self, tipo, clave, ascendente=True):
        """Ordena a partir de los datos originales. Regresa el resultado de ordenar()."""
        self._exigir_datos()
        resultado = ordenar(self.original, tipo, clave, ascendente)
        self.datos = resultado["datos"]
        self.ultimo = resultado
        self.tabla_hash = None      # los datos cambiaron: la tabla ya no sirve
        return resultado

    def buscar(self, metodo, valor):
        """Busca un valor. Regresa el resultado de buscar()."""
        self._exigir_datos()
        resultado = buscar(self.datos, metodo, valor, self.tabla_hash)
        self.tabla_hash = resultado["tabla_hash"]
        return resultado

    def primeros(self, cantidad=20):
        return self.datos[:cantidad]

    def ultimos(self, cantidad=20):
        return self.datos[max(0, len(self.datos) - cantidad):]

    def exportar(self, formato, nombre):
        """Guarda los datos actuales y un reporte. Regresa (ruta_datos, ruta_reporte)."""
        self._exigir_datos()
        return exportar(self.datos, self.nombre_archivo, formato, nombre, self.ultimo)

    def comparar(self):
        """Compara todos los algoritmos con los datos originales."""
        self._exigir_datos()
        return comparar(self.original, self.nombre_archivo)
