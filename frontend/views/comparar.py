"""Comparación de rendimiento de todos los algoritmos."""
import customtkinter as ctk

from frontend.components.cards import Banner, StatCard, Tabla, boton, etiqueta, panel
from frontend.views import VistaBase


class CompararView(VistaBase):
    TITULO = "Comparar algoritmos"
    SUBTITULO = "Ordena los mismos datos con todos los algoritmos y compara los tiempos."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        zona = ctk.CTkScrollableFrame(self, fg_color="transparent")
        zona.grid(row=0, column=0, sticky="nsew")
        zona.columnconfigure(0, weight=1)
        self._resultado = None
        self._version = app.version_carga

        p = panel(zona, "Comparación")
        p.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.nota = etiqueta(p.cuerpo, "", 12, suave=True, anchor="w", justify="left", wraplength=780)
        self.nota.pack(fill="x", pady=(0, 10))
        self.btn = self.registrar(boton(p.cuerpo, "Ejecutar comparación", self._comparar, ancho=210))
        self.btn.pack(anchor="w")

        self.banner = Banner(zona)
        self.banner.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.banner.ocultar()

        fila = ctk.CTkFrame(zona, fg_color="transparent")
        fila.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        fila.columnconfigure((0, 1, 2), weight=1, uniform="k")
        self.t_rapido = StatCard(fila, "Más rápido", "—", tam_valor=15)
        self.t_tiempo = StatCard(fila, "Su tiempo", "—", tam_valor=17)
        self.t_ok = StatCard(fila, "Verificación", "—", tam_valor=17)
        for i, t in enumerate((self.t_rapido, self.t_tiempo, self.t_ok)):
            t.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 2 else 7))

        pt = panel(zona, "Resultados")
        pt.grid(row=3, column=0, sticky="ew")
        self.tabla = Tabla(pt.cuerpo, [("Tipo", 2, "w"), ("Algoritmo", 5, "w"),
                                        ("Tiempo (s)", 3, "e"), ("Correcto", 2, "center")],
                           alto_fila=26, barra=True)
        self.tabla.pack(fill="x")
        self.tabla.llenar([])

    def _comparar(self):
        if not self.sesion.cargado:
            self.banner.mostrar("Primero carga un archivo en «Cargar archivo».", "aviso")
            return
        self.banner.ocultar()
        sesion = self.sesion
        version = self.app.version_carga

        def listo(resultado):
            self._resultado = resultado
            self._version = version
            self._pintar()
            r = resultado["mas_rapido"]
            self.banner.mostrar(f"Comparación terminada. Más rápido: {r['algoritmo']} ({r['segundos']:.6f} s).\n"
                                f"Tabla guardada en: {resultado['ruta']}", "exito")
            self.app.notificar("Comparación terminada.", "exito")

        self.app.ejecutar_tarea(sesion.comparar, listo,
                                "Comparando los algoritmos (puede tardar unos segundos)…",
                                lambda texto: self.banner.mostrar(texto, "error"))

    def _pintar(self):
        r = self._resultado
        filas = r["filas"]
        maximo = 0.0
        for f in filas:
            if f["segundos"] > maximo:
                maximo = f["segundos"]
        indice = 0
        for i, f in enumerate(filas):
            if f is r["mas_rapido"]:
                indice = i
        datos = [(f["tipo"], f["algoritmo"], f"{f['segundos']:.6f}", "sí" if f["correcto"] else "NO")
                 for f in filas]
        barras = [(f["segundos"] / maximo) if maximo > 0 else 0 for f in filas]
        self.tabla.llenar(datos, resaltar=indice, barras=barras)
        m = r["mas_rapido"]
        self.t_rapido.actualizar(m["algoritmo"], m["tipo"], "exito")
        self.t_tiempo.actualizar(f"{m['segundos']:.6f} s", f"{m['segundos'] * 1000:.3f} ms")
        todos = True
        for f in filas:
            if not f["correcto"]:
                todos = False
        self.t_ok.actualizar("Todos correctos" if todos else "Hay errores",
                             f"{len(filas)} algoritmos", "exito" if todos else "error")

    def al_mostrar(self):
        s = self.sesion
        if self._resultado is not None and self._version != self.app.version_carga:
            self._resultado = None                           # se cargó otro archivo
            self.tabla.llenar([])
            for t in (self.t_rapido, self.t_tiempo, self.t_ok):
                t.actualizar("—", "")
        self.btn.configure(state=self.estado(s.cargado))
        if s.cargado:
            self.nota.configure(text=f"Se ordenarán los {s.total:,} registros originales de forma ascendente con "
                                     "los algoritmos internos y externos. Las barras son proporcionales "
                                     "al tiempo del más lento.")
            if self.banner._texto.cget("text").startswith("Aún no hay datos"):
                self.banner.ocultar()
        else:
            self.nota.configure(text="Carga un archivo para poder comparar.")
            self.banner.mostrar("Aún no hay datos. Carga un archivo para comparar.", "info")
