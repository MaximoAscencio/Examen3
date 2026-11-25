"""
Pruebas funcionales de la interfaz gráfica de DATAFLOW.

Abre la aplicación real y maneja las pantallas por código (sin clics), pasando
por los mismos métodos que usan los botones y por los hilos de segundo plano.

    python pruebas_frontend.py

Necesita pantalla (en Linux sin escritorio: xvfb-run python pruebas_frontend.py).
No usa sort() ni sorted().
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import archivos
import backend
from frontend.app import DataflowApp
from frontend.views.ordenar import mismos_valores

DATOS = backend.CARPETA_DATOS
TXT_1000 = os.path.join(DATOS, "dataset_1000_duplicados.txt")
XLSX_5000 = os.path.join(DATOS, "dataset_5000_duplicados.xlsx")
TMP = os.path.join(backend.CARPETA_RESULTADOS, "_pruebas")

resultados = []


def verificar(nombre, condicion, detalle=""):
    resultados.append((nombre, bool(condicion)))
    print(f"  [{'OK' if condicion else 'FALLO'}] {nombre}" + (f"  -> {detalle}" if detalle and not condicion else ""))


def esperar(app, limite=180):
    """Procesa eventos hasta que termine la tarea en segundo plano."""
    inicio = time.time()
    app.update()
    while app.ocupado or not app._cola.empty():
        app.update()
        time.sleep(0.01)
        if time.time() - inicio > limite:
            raise TimeoutError("La tarea tardó demasiado")
    app.update()


def ordenada(datos, asc):
    for i in range(len(datos) - 1):
        if (asc and datos[i] > datos[i + 1]) or (not asc and datos[i] < datos[i + 1]):
            return False
    return True


def cargar(app, ruta):
    app.vistas["cargar"]._cargar(ruta)
    esperar(app)


def ordenar(app, tipo, clave, asc):
    v = app.vistas["ordenar"]
    v.sel_tipo.set("Interno" if tipo == "interno" else "Externo")
    v._cambio_tipo()
    for c, nombre in v._algoritmos:
        if c == clave:
            v.menu.set(nombre)
    v.sel_sentido.set("Ascendente" if asc else "Descendente")
    v._ordenar()
    esperar(app)


def buscar(app, metodo, texto):
    v = app.vistas["buscar"]
    v.sel.set(metodo.capitalize())
    v.entrada.delete(0, "end")
    v.entrada.insert(0, texto)
    v._buscar()
    app.update()


def main():
    os.makedirs(TMP, exist_ok=True)
    app = DataflowApp()
    s = app.sesion

    print("\n1. Estructura y sesión compartida")
    verificar("Las 7 vistas se crearon", len(app.vistas) == 7)
    verificar("Todas las vistas usan la misma Sesion", all(v.sesion is s for v in app.vistas.values()))
    for clave in app.vistas:
        app.mostrar(clave)
        app.update()
    verificar("Se puede navegar por todas las pantallas", True)

    print("\n2. Carga de archivos")
    cargar(app, TXT_1000)
    verificar("TXT de 1,000 registros", s.total == 1000, f"total={s.total}")
    cargar(app, XLSX_5000)
    verificar("XLSX de 5,000 registros", s.total == 5000, f"total={s.total}")
    antes = s.total
    cargar(app, os.path.join(TMP, "no_existe.txt"))
    verificar("Archivo inexistente: error y sesión intacta", s.total == antes)
    csv = os.path.join(TMP, "datos.csv")
    with open(csv, "w") as f:
        f.write("1\n2\n")
    cargar(app, csv)
    verificar("Formato no permitido: error y sesión intacta", s.total == antes)
    vacio = os.path.join(TMP, "vacio.txt")
    open(vacio, "w").close()
    cargar(app, vacio)
    verificar("Archivo vacío: error y sesión intacta", s.total == antes)
    mixto = os.path.join(TMP, "mixto.txt")
    with open(mixto, "w") as f:
        f.write("5\nabc\n3\n\n7.5\n3\n-2\n")
    cargar(app, mixto)
    verificar("Valores inválidos se ignoran y se cuentan",
              s.total == 4 and app.vistas["cargar"]._invalidas == 2,
              f"total={s.total}, invalidas={app.vistas['cargar']._invalidas}")

    print("\n3. Ordenamientos (TXT de 1,000 con duplicados)")
    cargar(app, TXT_1000)
    original = list(s.original)
    for tipo in ("interno", "externo"):
        for clave, _nombre in backend.algoritmos(tipo):
            for asc in (True, False):
                ordenar(app, tipo, clave, asc)
                bien = (ordenada(s.datos, asc) and mismos_valores(original, s.datos)
                        and s.ultimo["clave"] == clave)
                verificar(f"{tipo}/{clave} {'asc' if asc else 'desc'}", bien)
    verificar("Los datos originales no se alteran", s.original == original)
    verificar("La tarjeta de verificación indica 'Correcta'",
              app.vistas["ordenar"].t_verif._valor.cget("text") == "Correcta")

    print("\n4. Ordenamientos con XLSX de 5,000")
    cargar(app, XLSX_5000)
    original = list(s.original)
    for tipo, clave in (("interno", "quick"), ("interno", "radix"), ("externo", "mezcla_directa"),
                        ("externo", "mezcla_equilibrada")):
        ordenar(app, tipo, clave, True)
        verificar(f"{tipo}/{clave} con 5,000", ordenada(s.datos, True) and mismos_valores(original, s.datos))

    print("\n5. Búsquedas")
    cargar(app, TXT_1000)
    vb = app.vistas["buscar"]
    buscar(app, "binaria", str(s.datos[10]))
    verificar("Binaria sin ordenar muestra error", vb.banner.winfo_ismapped())
    buscar(app, "secuencial", "abc")
    verificar("Valor no numérico se rechaza", vb._historial == [])
    ordenar(app, "interno", "quick", True)
    existente = s.datos[137]
    ausente = s.datos[-1] + 1000
    for metodo in ("secuencial", "binaria", "hash"):
        buscar(app, metodo, str(existente))
        r = vb._historial[0]
        verificar(f"{metodo}: encuentra un valor existente", r[2].startswith("Encontrado"), str(r))
        buscar(app, metodo, str(ausente))
        verificar(f"{metodo}: no encuentra un valor ausente", vb._historial[0][2] == "No encontrado")
    r = s.buscar("hash", existente)
    verificar("Posición hash apunta al valor correcto", s.datos[r["posicion"]] == existente)
    contador = 0
    for x in s.datos:
        if x == existente:
            contador += 1
    verificar("Repeticiones hash = ocurrencias reales", r["repeticiones"] == contador,
              f"{r['repeticiones']} vs {contador}")
    ordenar(app, "interno", "heap", False)
    buscar(app, "binaria", str(existente))
    verificar("Binaria funciona con orden descendente", vb._historial[0][2].startswith("Encontrado"))

    print("\n6. Resultados (primeros / últimos 20)")
    vr = app.vistas["resultados"]
    app.mostrar("resultados")
    app.update()
    verificar("Tabla de primeros con 20 filas", len(vr.t_primeros._celdas) == 40)
    verificar("Tabla de últimos con 20 filas", len(vr.t_ultimos._celdas) == 40)
    verificar("Los valores mostrados coinciden con la sesión",
              vr.t_primeros._celdas[1].cget("text").strip() == str(s.datos[0]) and
              vr.t_ultimos._celdas[-1].cget("text").strip() == str(s.datos[-1]))

    print("\n7. Exportación")
    ve = app.vistas["exportar"]
    for formato in ("TXT", "XLSX"):
        ve.sel.set(formato)
        ve.entrada.delete(0, "end")
        ve.entrada.insert(0, "_pruebas/gui_exportado")
        ve._exportar()
        esperar(app)
        ruta = os.path.join(backend.CARPETA_RESULTADOS, "gui_exportado." + formato.lower())
        # el backend usa solo el nombre base, así que queda en resultados/
        ruta = os.path.join(backend.CARPETA_RESULTADOS, "gui_exportado." + formato.lower())
        existe = os.path.isfile(ruta)
        datos, _ = archivos.cargar_archivo(ruta) if existe else ([], 0)
        verificar(f"Exporta {formato} con los mismos datos", existe and datos == s.datos)
        verificar(f"Reporte de {formato}", os.path.isfile(os.path.join(backend.CARPETA_RESULTADOS,
                                                                       "gui_exportado_reporte.txt")))
        for extra in (ruta, os.path.join(backend.CARPETA_RESULTADOS, "gui_exportado_reporte.txt")):
            if os.path.isfile(extra):
                os.remove(extra)

    print("\n8. Comparación de algoritmos")
    cargar(app, TXT_1000)
    vc = app.vistas["comparar"]
    vc._comparar()
    esperar(app)
    verificar("La comparación devolvió 9 algoritmos (7 internos + 2 externos)", vc._resultado and len(vc._resultado["filas"]) == 9)
    verificar("Todos los algoritmos correctos", all(f["correcto"] for f in vc._resultado["filas"]))
    verificar("La tabla muestra 9 filas", len(vc.tabla._celdas) == 9 * 5)

    print("\n9. Operaciones simultáneas y persistencia")
    ok = app.ejecutar_tarea(lambda: time.sleep(0.5), lambda _r: None, "prueba")
    segundo = app.ejecutar_tarea(lambda: None, lambda _r: None, "otra")
    verificar("Segunda tarea simultánea rechazada", ok and not segundo)
    verificar("Botones bloqueados durante la tarea", str(app.vistas["ordenar"].btn.cget("state")) == "disabled")
    esperar(app)
    verificar("Botones liberados al terminar", str(app.vistas["ordenar"].btn.cget("state")) == "normal")
    datos_antes = list(s.datos)
    for clave in app.vistas:
        app.mostrar(clave)
        app.update()
    verificar("Cambiar de pantalla no pierde datos", s.datos == datos_antes and
              vc._resultado is not None)
    cargar(app, XLSX_5000)
    app.mostrar("comparar")
    verificar("Cargar otro archivo reinicia la comparación anterior", vc._resultado is None)

    app.destroy()
    fallos = [n for n, ok_ in resultados if not ok_]
    print(f"\nPruebas: {len(resultados)} | Fallos: {len(fallos)}")
    for n in fallos:
        print("  FALLO:", n)
    print("RESULTADO:", "todas las pruebas pasaron." if not fallos else "hay fallos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
