"""Primeros y últimos 20 registros de los datos actuales."""
import customtkinter as ctk

from frontend.components.cards import Banner, Tabla, etiqueta, panel
from frontend.views import VistaBase

CANTIDAD = 20


class ResultadosView(VistaBase):
    TITULO = "Resultados"
    SUBTITULO = "Primeros y últimos 20 registros de los datos actuales."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        zona = ctk.CTkScrollableFrame(self, fg_color="transparent")
        zona.grid(row=0, column=0, sticky="nsew")
        zona.columnconfigure((0, 1), weight=1, uniform="t")

        self.banner = Banner(zona)
        self.banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.banner.ocultar()
        self.resumen = etiqueta(zona, "", 13, suave=True, anchor="w")
        self.resumen.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        cols = [("Posición", 1, "center"), ("Valor", 2, "e")]
        p1 = panel(zona, f"Primeros {CANTIDAD}")
        p1.grid(row=2, column=0, sticky="nsew", padx=(0, 7))
        self.t_primeros = Tabla(p1.cuerpo, cols, alto_fila=24)
        self.t_primeros.pack(fill="x")
        p2 = panel(zona, f"Últimos {CANTIDAD}")
        p2.grid(row=2, column=1, sticky="nsew", padx=(7, 0))
        self.t_ultimos = Tabla(p2.cuerpo, cols, alto_fila=24)
        self.t_ultimos.pack(fill="x")

    def al_mostrar(self):
        s = self.sesion
        if not s.cargado:
            self.banner.mostrar("Aún no hay datos. Carga un archivo para ver los resultados.", "info")
            self.resumen.configure(text="")
            self.t_primeros.llenar([])
            self.t_ultimos.llenar([])
            return
        self.banner.ocultar()
        if s.ordenado:
            u = s.ultimo
            estado = (f"ordenados con {u['algoritmo']} "
                      f"({'ascendente' if u['ascendente'] else 'descendente'})")
        else:
            estado = "sin ordenar (tal como se cargaron)"
        self.resumen.configure(text=f"{s.nombre_archivo} · {s.total:,} registros · {estado}")
        primeros = s.primeros(CANTIDAD)
        ultimos = s.ultimos(CANTIDAD)
        inicio = s.total - len(ultimos) + 1
        self.t_primeros.llenar([(i + 1, v) for i, v in enumerate(primeros)])
        self.t_ultimos.llenar([(inicio + i, v) for i, v in enumerate(ultimos)])
