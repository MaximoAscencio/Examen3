"""
Librería de BÚSQUEDAS: secuencial, binaria y hash.

Todas trabajan con listas de números enteros y regresan posiciones que
empiezan en 0 (-1 significa "no encontrado").

La búsqueda binaria NO ordena la lista por su cuenta: necesita recibirla ya
ordenada (con las librerías de ordenamiento del equipo).

Reglas del examen: no se usan los métodos de ordenamiento automáticos de Python.
"""


# ----------------------------------------------------------------------
# Utilidad
# ----------------------------------------------------------------------

def esta_ordenada(lista, ascendente=True):
    """True si la lista está ordenada en el sentido indicado."""
    for i in range(len(lista) - 1):
        if ascendente and lista[i] > lista[i + 1]:
            return False
        if not ascendente and lista[i] < lista[i + 1]:
            return False
    return True


# ----------------------------------------------------------------------
# Búsqueda secuencial
# ----------------------------------------------------------------------

def busqueda_secuencial(lista, objetivo):
    """Recorre la lista de principio a fin. Regresa la primera posición
    donde aparece el objetivo, o -1."""
    for i in range(len(lista)):
        if lista[i] == objetivo:
            return i
    return -1


# ----------------------------------------------------------------------
# Búsqueda binaria
# ----------------------------------------------------------------------

def busqueda_binaria(lista, objetivo, ascendente=True):
    """Busca en una lista YA ORDENADA. Si el valor está repetido regresa su
    primera aparición. Regresa -1 si no existe."""
    inicio = 0
    final = len(lista) - 1
    encontrado = -1

    while inicio <= final:
        medio = (inicio + final) // 2

        if lista[medio] == objetivo:
            encontrado = medio
            final = medio - 1        # seguir a la izquierda: primera aparición
        else:
            if ascendente:
                ir_derecha = lista[medio] < objetivo
            else:
                ir_derecha = lista[medio] > objetivo
            if ir_derecha:
                inicio = medio + 1
            else:
                final = medio - 1

    return encontrado


# ----------------------------------------------------------------------
# Búsqueda por hash (tabla hash propia con encadenamiento)
# ----------------------------------------------------------------------

class TablaHash:
    """Tabla hash con encadenamiento para números enteros.

    Cada clave guarda la lista de posiciones donde aparece en los datos."""

    def __init__(self, tamanio=1009):
        self.tamanio = tamanio
        self.tabla = [[] for _ in range(tamanio)]

    def funcion_hash(self, clave):
        """Módulo del número entre el tamaño de la tabla (sirve con negativos)."""
        return clave % self.tamanio

    def insertar(self, clave, posicion):
        cubeta = self.tabla[self.funcion_hash(clave)]
        for par in cubeta:
            if par[0] == clave:
                par[1].append(posicion)      # valor repetido: otra posición
                return
        cubeta.append([clave, [posicion]])

    def buscar(self, clave):
        """Regresa la lista de posiciones del valor (vacía si no existe)."""
        cubeta = self.tabla[self.funcion_hash(clave)]
        for par in cubeta:
            if par[0] == clave:
                return par[1]
        return []


def construir_tabla_hash(lista):
    """Construye una tabla hash con todos los datos de la lista."""
    tamanio = max(11, len(lista) // 2) | 1       # tamaño impar, proporcional a los datos
    tabla = TablaHash(tamanio)
    for posicion in range(len(lista)):
        tabla.insertar(lista[posicion], posicion)
    return tabla


def busqueda_hash(tabla, objetivo):
    """Regresa la primera posición del objetivo, o -1."""
    posiciones = tabla.buscar(objetivo)
    if posiciones:
        return posiciones[0]
    return -1
