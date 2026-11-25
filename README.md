# Examen 3 — Sistema de Procesamiento y Ordenamiento Masivo de Datos

Examen parcial de **Algoritmos de ordenamiento y búsqueda** (Estructura de Datos).
Programa en Python que carga números desde archivos TXT o XLSX, los ordena con
algoritmos propios (internos y externos), busca valores y exporta los resultados.

## Requisitos

- Python 3.9 o superior
- La librería `openpyxl` (para leer y escribir XLSX)

```
pip install -r requirements.txt
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```
python main.py
```

Para correr las pruebas automáticas:

```
python pruebas.py
```

## Menú del programa

| Opción | Qué hace |
|---|---|
| 1. Cargar archivo | Elige un TXT o XLSX (los de la carpeta `datos/` o cualquier ruta) |
| 2. Ordenar datos | Elige tipo (interno/externo), algoritmo y orden (ascendente/descendente) |
| 3. Buscar un valor | Secuencial, binaria (requiere datos ordenados) o hash |
| 4. Mostrar resultados | Primeros 20, últimos 20 y total de registros |
| 5. Exportar resultados | Guarda el archivo ordenado (TXT o XLSX) y un reporte con algoritmo y tiempo |
| 6. Comparar algoritmos | Ejecuta todos los algoritmos y compara sus tiempos |

Los archivos exportados se guardan en la carpeta `resultados/`.

## Estructura del proyecto

```
main.py                      Interfaz de consola (solo pide datos y muestra resultados)
backend.py                   Lógica del sistema: lo que usa cualquier interfaz (consola, ventana...)
archivos.py                  Lectura y escritura de TXT y XLSX
ordenamientos_internos.py    Librería: burbuja, selección, inserción, shell, quick, heap, radix
ordenamientos_externos.py    Librería: mezcla directa, mezcla equilibrada natural, intercalación
busquedas.py                 Librería: secuencial, binaria y tabla hash propia
pruebas.py                   Pruebas automáticas
datos/                       dataset_1000_duplicados.txt, dataset_5000_duplicados.xlsx
resultados/                  Archivos exportados
```

## Backend y frontend

El programa está separado en dos capas:

- **Backend** (`backend.py` y las librerías): toda la lógica. Sin `input()` ni `print()`:
  las funciones reciben datos, regresan resultados y, si algo falla, lanzan una excepción
  con un mensaje en español listo para mostrarse.
- **Frontend** (`main.py` para consola, o cualquier ventana): solo pide datos al usuario
  y muestra lo que el backend regresa.

La forma más fácil de usar el backend desde una interfaz es la clase `Sesion`:

```python
from backend import Sesion

s = Sesion()
s.cargar("datos/dataset_1000_duplicados.txt")      # regresa cuántos valores se ignoraron
r = s.ordenar("interno", "quick", ascendente=True) # tipo: "interno" o "externo"
r["segundos"], r["algoritmo"], r["pasadas"], r["correcto"]
s.primeros(20), s.ultimos(20), s.total
b = s.buscar("binaria", 4521)                      # "secuencial", "binaria" o "hash"
b["posicion"], b["segundos"], b["repeticiones"]    # posición empieza en 0; -1 = no existe
s.exportar("xlsx", "mis_datos")                    # regresa (ruta_datos, ruta_reporte)
s.comparar()["lineas"]                             # tabla comparativa de todos los algoritmos
```

Para llenar menús en la interfaz: `backend.TIPOS_ORDENAMIENTO`, `backend.algoritmos("interno")`,
`backend.algoritmos("externo")`, `backend.METODOS_BUSQUEDA`, `backend.FORMATOS_SALIDA` y
`backend.listar_archivos_datos()`. Para mostrar tiempos: `backend.formato_tiempo(segundos)`.

Errores: `ValueError`, `FileNotFoundError` y `OSError` con mensaje en español
(por ejemplo, buscar con búsqueda binaria sin ordenar antes).

Los ordenamientos siempre parten de los datos **originales** cargados; así se pueden probar
varios algoritmos seguidos y comparar sus tiempos.

## Librerías propias

Los algoritmos son los desarrollados por el equipo en tareas anteriores
(`Ordenamiento/`, `ordenamientos1_anaya/`, `ADA3 - MetOrdenaExt/`),
reunidos en librerías con una interfaz común:

```python
from ordenamientos_internos import ordenar_interno
from ordenamientos_externos import ordenar_externo
from busquedas import busqueda_secuencial, busqueda_binaria, construir_tabla_hash, busqueda_hash

ordenar_interno(lista, "quick", ascendente=True)          # regresa una lista nueva
ordenar_externo("entrada.txt", "salida.txt", "mezcla_directa", ascendente=False)
```

### Ordenamientos internos (en memoria)

Burbuja, Selección, Inserción, Shell Sort, Quick Sort, Heap Sort y Radix Sort.

### Ordenamientos externos (con archivos)

- **Mezcla directa:** reparte los datos en dos archivos por bloques de longitud fija
  (1, 2, 4, 8...) y los fusiona hasta tener un solo bloque.
- **Mezcla equilibrada natural:** aprovecha los tramos que ya vienen ordenados y usa
  cuatro archivos auxiliares (dos de entrada y dos de salida) que se alternan.

Los archivos auxiliares se crean en una carpeta temporal `_tmp_...` y se borran al terminar.

### Búsquedas

- **Secuencial:** recorre la lista de principio a fin. O(n).
- **Binaria:** divide la lista ordenada a la mitad en cada paso. O(log n). Regresa la
  primera aparición si el valor está repetido.
- **Hash:** tabla hash propia con encadenamiento; guarda todas las posiciones de cada
  valor. Búsqueda en tiempo promedio O(1).

## Restricciones del examen

- No se usa `.sort()`, `sorted()` ni librerías automáticas de ordenamiento
  (`pruebas.py` lo verifica).
- Solo se usan `os`, `time`, `openpyxl` y funciones estándar de Python.
- El orden descendente se obtiene ordenando de menor a mayor y recorriendo el
  resultado de extremo a extremo con un intercambio manual (en los internos), o
  invirtiendo el criterio de comparación (en los externos).

## Comparación básica (borrador)

| Escenario | Algoritmo recomendado | Por qué |
|---|---|---|
| Datos pequeños | Inserción | Simple y muy rápido con pocos datos |
| Datos masivos | Quick Sort o Heap Sort (Radix si son enteros) | O(n log n); Radix es lineal en enteros |
| Archivos externos | Mezcla equilibrada natural | Recorre los archivos de forma secuencial y aprovecha tramos ordenados |
| Datos parcialmente ordenados | Inserción o mezcla natural | Su costo baja cuando ya hay orden |
| Búsquedas frecuentes | Hash (o ordenar una vez y usar binaria) | O(1) y O(log n) contra O(n) de la secuencial |

Los tiempos reales de cada algoritmo se obtienen con la opción 6 del menú.

## Equipo

Equipo de 6 integrantes — Instituto Tecnológico de Mérida, ISC, grupo 3SA.
