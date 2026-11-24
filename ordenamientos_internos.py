"""
Librería de ordenamientos INTERNOS (los datos se ordenan en memoria).

Los algoritmos son los que el equipo desarrolló en tareas anteriores:
    - Burbuja, Inserción y Selección  (carpeta Ordenamiento/)
    - Shell, Quick, Heap y Radix      (carpeta ordenamientos1_anaya/)
Aquí se reúnen en una sola librería con una interfaz común.

Uso:
    from ordenamientos_internos import ordenar_interno
    resultado = ordenar_interno(lista, "quick", ascendente=True)

Reglas del examen: no se usan los métodos de ordenamiento automáticos de Python.
"""


# ----------------------------------------------------------------------
# Algoritmos (lógica original del equipo; modifican la lista que reciben)
# ----------------------------------------------------------------------

def burbuja(lista):
    n = len(lista)

    for i in range(n):
        for j in range(0, n - i - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]

    return lista


def seleccion(lista):
    n = len(lista)

    for i in range(n):
        menor = i

        for j in range(i + 1, n):
            if lista[j] < lista[menor]:
                menor = j

        lista[i], lista[menor] = lista[menor], lista[i]

    return lista


def insercion(lista):
    for i in range(1, len(lista)):
        actual = lista[i]
        j = i - 1

        while j >= 0 and lista[j] > actual:
            lista[j + 1] = lista[j]
            j -= 1

        lista[j + 1] = actual

    return lista


def shell_sort(numeros):
    """Ordena con inserciones separadas por saltos cada vez menores."""
    salto = len(numeros) // 2
    while salto > 0:
        for indice in range(salto, len(numeros)):
            valor = numeros[indice]
            posicion = indice
            while posicion >= salto and numeros[posicion - salto] > valor:
                numeros[posicion] = numeros[posicion - salto]
                posicion -= salto
            numeros[posicion] = valor
        salto //= 2


def particionar(numeros, inicio, fin):
    """Coloca el último elemento como pivote en su posición final."""
    pivote = numeros[fin]
    frontera = inicio
    for indice in range(inicio, fin):
        if numeros[indice] < pivote:
            numeros[frontera], numeros[indice] = numeros[indice], numeros[frontera]
            frontera += 1
    numeros[frontera], numeros[fin] = numeros[fin], numeros[frontera]
    return frontera


def quick_sort(numeros):
    """Ordena los rangos mediante una pila de particiones pendientes."""
    pendientes = [(0, len(numeros) - 1)]
    while pendientes:
        inicio, fin = pendientes.pop()
        if inicio < fin:
            pivote = particionar(numeros, inicio, fin)
            if inicio < pivote - 1:
                pendientes.append((inicio, pivote - 1))
            if pivote + 1 < fin:
                pendientes.append((pivote + 1, fin))


def hundir(numeros, raiz, limite):
    """Restaura el montículo máximo en el rango anterior a limite."""
    while 2 * raiz + 1 < limite:
        mayor = 2 * raiz + 1
        derecho = mayor + 1
        if derecho < limite and numeros[derecho] > numeros[mayor]:
            mayor = derecho
        if numeros[raiz] >= numeros[mayor]:
            break
        numeros[raiz], numeros[mayor] = numeros[mayor], numeros[raiz]
        raiz = mayor


def heap_sort(numeros):
    """Construye un montículo máximo y coloca cada máximo al final."""
    cantidad = len(numeros)
    for raiz in range(cantidad // 2 - 1, -1, -1):
        hundir(numeros, raiz, cantidad)

    for fin in range(cantidad - 1, 0, -1):
        numeros[0], numeros[fin] = numeros[fin], numeros[0]
        hundir(numeros, 0, fin)


def radix_sort(numeros):
    """Ordena por dígitos y aplica un desplazamiento para admitir negativos."""
    if not numeros:
        return

    desplazamiento = max(0, -min(numeros))
    maximo = max(numeros) + desplazamiento
    posicion_decimal = 1
    while maximo // posicion_decimal > 0:
        grupos = [[] for _ in range(10)]
        for numero in numeros:
            digito = ((numero + desplazamiento) // posicion_decimal) % 10
            grupos[digito].append(numero)

        # Conservamos el orden de llegada dentro de cada grupo.
        numeros[:] = [numero for grupo in grupos for numero in grupo]
        posicion_decimal *= 10


# ----------------------------------------------------------------------
# Interfaz común
# ----------------------------------------------------------------------

# clave -> (nombre para mostrar, función)
ALGORITMOS = {
    "burbuja": ("Burbuja (Bubble Sort)", burbuja),
    "seleccion": ("Selección (Selection Sort)", seleccion),
    "insercion": ("Inserción (Insertion Sort)", insercion),
    "shell": ("Shell Sort", shell_sort),
    "quick": ("Quick Sort", quick_sort),
    "heap": ("Heap Sort", heap_sort),
    "radix": ("Radix Sort", radix_sort),
}

# Orden en el que se muestran en los menús.
CLAVES = ["burbuja", "seleccion", "insercion", "shell", "quick", "heap", "radix"]


def invertir(lista):
    """Invierte la lista en sitio (intercambiando extremos), sin reversed()."""
    izquierda = 0
    derecha = len(lista) - 1
    while izquierda < derecha:
        lista[izquierda], lista[derecha] = lista[derecha], lista[izquierda]
        izquierda += 1
        derecha -= 1
    return lista


def ordenar_interno(lista, algoritmo, ascendente=True):
    """Regresa una NUEVA lista ordenada; la lista recibida no se modifica.

    algoritmo: una de las claves de ALGORITMOS.
    ascendente: True = de menor a mayor, False = de mayor a menor.
    """
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo interno desconocido: {algoritmo}")

    datos = list(lista)
    funcion = ALGORITMOS[algoritmo][1]
    resultado = funcion(datos)
    if resultado is None:          # shell, quick, heap y radix ordenan en sitio
        resultado = datos
    if not ascendente:
        invertir(resultado)
    return resultado
