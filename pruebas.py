"""
Pruebas automáticas de las librerías del equipo.

Ejecutar:  python pruebas.py

Comprueba, con los dos datasets del examen y con casos límite, que:
  - todos los ordenamientos internos y externos funcionan (ascendente y descendente),
  - las tres búsquedas encuentran los mismos resultados,
  - la lectura/escritura de TXT y XLSX es correcta,
  - el código no usa los métodos de ordenamiento prohibidos por el examen.
"""

import os
import time

import archivos
import backend
import busquedas
import ordenamientos_externos as externos
import ordenamientos_internos as internos

BASE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(BASE, "datos")
PRUEBAS = os.path.join(BASE, "resultados", "_pruebas")

total = 0
fallos = 0


def comprobar(descripcion, condicion):
    global total, fallos
    total += 1
    if not condicion:
        fallos += 1
        print(f"  FALLO: {descripcion}")


def conteo(lista):
    """Cuenta cuántas veces aparece cada valor (para comparar sin ordenar)."""
    cuenta = {}
    for x in lista:
        cuenta[x] = cuenta.get(x, 0) + 1
    return cuenta


def es_resultado_correcto(original, resultado, ascendente):
    """Mismos elementos que el original y en el orden pedido."""
    return (len(resultado) == len(original)
            and busquedas.esta_ordenada(resultado, ascendente)
            and conteo(resultado) == conteo(original))


def lista_pseudoaleatoria(n, semilla=7):
    valores = []
    x = semilla
    for _ in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        valores.append(x % 2001 - 1000)
    return valores


def casos_limite():
    return {
        "lista vacía": [],
        "un elemento": [5],
        "todos iguales": [3] * 9,
        "negativos y repetidos": [-5, 3, -1, 0, -5, 9, -100, 100],
        "orden inverso": list(range(300, 0, -1)),
        "ya ordenada": list(range(300)),
        "pseudoaleatoria": lista_pseudoaleatoria(500),
    }


def probar_ordenamientos(nombre, datos):
    os.makedirs(PRUEBAS, exist_ok=True)
    entrada = os.path.join(PRUEBAS, "entrada.txt")
    salida = os.path.join(PRUEBAS, "salida.txt")
    archivos.escribir_txt(entrada, datos)
    for ascendente in (True, False):
        orden = "asc" if ascendente else "desc"
        for clave in internos.CLAVES:
            copia = list(datos)
            resultado = internos.ordenar_interno(datos, clave, ascendente)
            comprobar(f"{clave} {orden} con {nombre}",
                      es_resultado_correcto(datos, resultado, ascendente))
            comprobar(f"{clave} no debe modificar la lista original ({nombre})",
                      datos == copia)
        for clave in externos.CLAVES:
            externos.ordenar_externo(entrada, salida, clave, ascendente)
            resultado, _ = archivos.leer_txt(salida)
            comprobar(f"{clave} {orden} con {nombre}",
                      es_resultado_correcto(datos, resultado, ascendente))
    comprobar(f"el externo no debe dejar carpetas temporales ({nombre})",
              not any(n.startswith("_tmp_") for n in os.listdir(PRUEBAS)))


def probar_busquedas(nombre, datos):
    ordenada = internos.ordenar_interno(datos, "quick", True)
    descendente = internos.ordenar_interno(datos, "quick", False)
    tabla = busquedas.construir_tabla_hash(datos)
    candidatos = list(datos[:150]) + [-100000, 0, 99999999]
    for valor in candidatos:
        sec = busquedas.busqueda_secuencial(datos, valor)
        has = busquedas.busqueda_hash(tabla, valor)
        comprobar(f"secuencial y hash coinciden para {valor} ({nombre})", sec == has)
        for lista, asc in ((ordenada, True), (descendente, False)):
            pos = busquedas.busqueda_binaria(lista, valor, asc)
            if sec == -1:
                comprobar(f"binaria no debe encontrar {valor} ({nombre})", pos == -1)
            else:
                correcta = (pos != -1 and lista[pos] == valor
                            and (pos == 0 or lista[pos - 1] != valor))
                comprobar(f"binaria halla la primera aparición de {valor} ({nombre})", correcta)
    for valor in candidatos[:20]:
        comprobar(f"la tabla hash cuenta las repeticiones de {valor} ({nombre})",
                  len(tabla.buscar(valor)) == conteo(datos).get(valor, 0))


def probar_archivos():
    os.makedirs(PRUEBAS, exist_ok=True)
    datos = [4, -2, 9, 4, 0]
    for ext in (".txt", ".xlsx"):
        ruta = os.path.join(PRUEBAS, "ida_y_vuelta" + ext)
        archivos.guardar_datos(ruta, datos)
        leidos, invalidas = archivos.cargar_archivo(ruta)
        comprobar(f"ida y vuelta {ext}", leidos == datos and invalidas == 0)
    sucio = os.path.join(PRUEBAS, "sucio.txt")
    with open(sucio, "w", encoding="utf-8") as f:
        f.write("1\n\nabc\n2\n3.5\n4\n")
    leidos, invalidas = archivos.cargar_archivo(sucio)
    comprobar("TXT con líneas inválidas", leidos == [1, 2, 4] and invalidas == 2)
    try:
        archivos.cargar_archivo(os.path.join(PRUEBAS, "no_existe.txt"))
        comprobar("archivo inexistente debe fallar", False)
    except FileNotFoundError:
        comprobar("archivo inexistente debe fallar", True)
    try:
        archivos.cargar_archivo(os.path.join(BASE, "README.md"))
        comprobar("formato no permitido debe fallar", False)
    except ValueError:
        comprobar("formato no permitido debe fallar", True)


def probar_bloqueos_de_windows():
    """Simula que Windows bloquea el archivo de salida (OneDrive, antivirus)."""
    os.makedirs(PRUEBAS, exist_ok=True)
    datos = [5, 3, 9, 1, 7, 3, 8, 2]
    entrada = os.path.join(PRUEBAS, "bloq_entrada.txt")
    salida = os.path.join(PRUEBAS, "bloq_salida.txt")
    archivos.escribir_txt(entrada, datos)
    real = os.replace
    espera = externos.ESPERA_BLOQUEO
    externos.ESPERA_BLOQUEO = 0.01

    def bloqueo_temporal(origen, destino):
        bloqueo_temporal.llamadas += 1
        if bloqueo_temporal.llamadas <= 2:
            raise PermissionError(5, "Acceso denegado")
        return real(origen, destino)

    def bloqueo_permanente(origen, destino):
        raise PermissionError(5, "Acceso denegado")

    try:
        for nombre, falso in (("bloqueo breve", bloqueo_temporal),
                              ("bloqueo permanente del reemplazo", bloqueo_permanente)):
            for algoritmo in externos.CLAVES:
                bloqueo_temporal.llamadas = 0
                os.replace = falso
                try:
                    externos.ordenar_externo(entrada, salida, algoritmo, True)
                finally:
                    os.replace = real
                resultado, _ = archivos.leer_txt(salida)
                comprobar(f"{algoritmo} con {nombre}",
                          es_resultado_correcto(datos, resultado, True))
                comprobar(f"{algoritmo} con {nombre}: sin carpetas temporales",
                          not any(n.startswith("_tmp_") for n in os.listdir(PRUEBAS)))
    finally:
        os.replace = real
        externos.ESPERA_BLOQUEO = espera


def probar_backend():
    """Recorre el flujo completo del backend, como lo haría cualquier interfaz."""
    ruta_xlsx = os.path.join(DATOS, "dataset_5000_duplicados.xlsx")
    if not os.path.isfile(ruta_xlsx):
        return
    s = backend.Sesion()
    comprobar("sesión nueva sin datos", not s.cargado and s.total == 0)
    for accion in (lambda: s.ordenar("interno", "quick"),
                   lambda: s.buscar("secuencial", 1),
                   lambda: s.exportar("txt", "x"),
                   lambda: s.comparar()):
        try:
            accion()
            comprobar("sin datos cargados debe fallar", False)
        except ValueError:
            comprobar("sin datos cargados debe fallar", True)

    try:
        s.cargar(os.path.join(PRUEBAS, "no_existe.txt"))
        comprobar("cargar archivo inexistente debe fallar", False)
    except (OSError, ValueError):
        comprobar("cargar archivo inexistente debe fallar", True)
    comprobar("un intento fallido no deja la sesión cargada", not s.cargado)

    invalidas = s.cargar(ruta_xlsx)
    comprobar("sesión carga 5000 registros", s.total == 5000 and invalidas == 0)
    comprobar("primeros y últimos son 20", len(s.primeros()) == 20 and len(s.ultimos()) == 20)
    original = list(s.original)

    try:
        s.buscar("binaria", original[0])
        comprobar("binaria sin ordenar debe fallar", False)
    except ValueError:
        comprobar("binaria sin ordenar debe fallar", True)

    for tipo in ("interno", "externo"):
        for clave, _ in backend.algoritmos(tipo):
            for asc in (True, False):
                r = s.ordenar(tipo, clave, asc)
                comprobar(f"backend {tipo}/{clave}/{asc}",
                          r["correcto"] and es_resultado_correcto(original, s.datos, asc))
                comprobar("la sesión conserva los datos originales", s.original == original)
                valor = original[100]
                bus = s.buscar("binaria", valor)
                comprobar("binaria en la sesión", bus["posicion"] != -1
                          and s.datos[bus["posicion"]] == valor)
                hs = s.buscar("hash", valor)
                comprobar("hash en la sesión", hs["posicion"] == bus["posicion"]
                          and hs["repeticiones"] == conteo(original)[valor])
    # tabla hash reutilizada y reconstruida
    s.ordenar("interno", "radix", True)
    primera = s.buscar("hash", original[0])
    segunda = s.buscar("hash", original[1])
    comprobar("la tabla hash se construye una vez",
              primera["segundos_construccion"] is not None
              and segunda["segundos_construccion"] is None)
    s.ordenar("interno", "heap", True)
    tercera = s.buscar("hash", original[0])
    comprobar("al reordenar se reconstruye la tabla hash",
              tercera["segundos_construccion"] is not None)
    comprobar("valor inexistente", s.buscar("secuencial", -123456)["posicion"] == -1)
    try:
        s.buscar("magica", 1)
        comprobar("método de búsqueda inválido debe fallar", False)
    except ValueError:
        comprobar("método de búsqueda inválido debe fallar", True)
    try:
        s.ordenar("interno", "no_existe")
        comprobar("algoritmo inválido debe fallar", False)
    except ValueError:
        comprobar("algoritmo inválido debe fallar", True)

    # exportar
    s.ordenar("externo", "mezcla_directa", False)
    for formato in ("txt", "xlsx"):
        ruta_datos, ruta_reporte = s.exportar(formato, "_prueba_exportado")
        leidos, _ = archivos.cargar_archivo(ruta_datos)
        comprobar(f"exportar {formato}: mismo contenido y orden",
                  leidos == s.datos and busquedas.esta_ordenada(leidos, False))
        with open(ruta_reporte, encoding="utf-8") as f:
            texto = f.read()
        comprobar("el reporte trae algoritmo, orden y tiempo",
                  "Mezcla directa" in texto and "descendente" in texto
                  and "Tiempo de ejecución" in texto)
    try:
        backend.exportar([1], "x", "pdf", "y")
        comprobar("formato de salida inválido debe fallar", False)
    except ValueError:
        comprobar("formato de salida inválido debe fallar", True)

    # comparar
    s.cargar(os.path.join(DATOS, "dataset_1000_duplicados.txt")) if os.path.isfile(
        os.path.join(DATOS, "dataset_1000_duplicados.txt")) else None
    r = s.comparar()
    comprobar("la comparación trae los 9 algoritmos", len(r["filas"]) == 9)
    comprobar("todos correctos en la comparación", all(f["correcto"] for f in r["filas"]))
    comprobar("se guardó la tabla comparativa", os.path.isfile(r["ruta"]))


def probar_codigo_prohibido():
    # Los patrones se arman por partes para que este archivo no los contenga.
    prohibidos = ["so" + "rted(", ".so" + "rt("]
    modulos = ["main.py", "backend.py", "archivos.py", "busquedas.py",
               "ordenamientos_internos.py", "ordenamientos_externos.py", "pruebas.py"]
    for modulo in modulos:
        with open(os.path.join(BASE, modulo), encoding="utf-8") as f:
            texto = f.read()
        for patron in prohibidos:
            comprobar(f"{modulo} no debe usar {patron}", patron not in texto)


def _reintentar(accion, ruta, intentos=10, espera=0.3):
    """En Windows/OneDrive una carpeta puede quedar bloqueada un instante."""
    for i in range(intentos):
        try:
            accion(ruta)
            return
        except PermissionError:
            if i == intentos - 1:
                print(f"AVISO: no se pudo borrar {ruta} (en uso). Bórralo a mano.")
                return
            time.sleep(espera)


def limpiar():
    """Borra los archivos que generan las pruebas en resultados/."""
    carpeta = os.path.dirname(PRUEBAS)
    if not os.path.isdir(carpeta):
        return
    if os.path.isdir(PRUEBAS):
        for nombre in os.listdir(PRUEBAS):
            _reintentar(os.remove, os.path.join(PRUEBAS, nombre))
        _reintentar(os.rmdir, PRUEBAS)
    for nombre in os.listdir(carpeta):
        generado = (nombre.startswith("_prueba_")
                    or nombre in ("entrada_externa.txt", "salida_externa.txt",
                                  "comparacion_1000_registros.txt"))
        if generado and os.path.isfile(os.path.join(carpeta, nombre)):
            _reintentar(os.remove, os.path.join(carpeta, nombre))
    if not os.listdir(carpeta):
        _reintentar(os.rmdir, carpeta)


def main():
    conjuntos = {}
    ruta_txt = os.path.join(DATOS, "dataset_1000_duplicados.txt")
    ruta_xlsx = os.path.join(DATOS, "dataset_5000_duplicados.xlsx")
    if os.path.isfile(ruta_txt):
        conjuntos["dataset 1000 (TXT)"], _ = archivos.cargar_archivo(ruta_txt)
    if os.path.isfile(ruta_xlsx):
        conjuntos["dataset 5000 (XLSX)"], _ = archivos.cargar_archivo(ruta_xlsx)
    if "dataset 1000 (TXT)" in conjuntos:
        comprobar("el TXT trae 1000 números", len(conjuntos["dataset 1000 (TXT)"]) == 1000)
    if "dataset 5000 (XLSX)" in conjuntos:
        comprobar("el XLSX trae 5000 números", len(conjuntos["dataset 5000 (XLSX)"]) == 5000)
    conjuntos.update(casos_limite())

    try:
        for nombre, datos in conjuntos.items():
            print(f"Probando ordenamientos con: {nombre}")
            probar_ordenamientos(nombre, datos)
        for nombre in ("dataset 1000 (TXT)", "dataset 5000 (XLSX)", "negativos y repetidos",
                       "todos iguales", "pseudoaleatoria"):
            if nombre in conjuntos:
                print(f"Probando búsquedas con: {nombre}")
                probar_busquedas(nombre, conjuntos[nombre])
        print("Probando lectura y escritura de archivos")
        probar_archivos()
        print("Probando bloqueos de archivos como en Windows/OneDrive")
        probar_bloqueos_de_windows()
        print("Probando el backend (sesión completa)")
        probar_backend()
        print("Revisando que no se usen métodos de ordenamiento prohibidos")
        probar_codigo_prohibido()
    finally:
        limpiar()

    print(f"\nPruebas realizadas: {total}")
    if fallos == 0:
        print("RESULTADO: todas las pruebas pasaron.")
    else:
        print(f"RESULTADO: {fallos} prueba(s) fallaron.")
    return fallos


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
