"""Buscar un valor: secuencial, binaria o hash."""
import customtkinter as ctk

from frontend.components.cards import Banner, StatCard, Tabla, boton, etiqueta, panel
from frontend.config import COLORES, fuente
from frontend.views import VistaBase

METODOS = {"Secuencial": "secuencial", "Binaria": "binaria", "Hash": "hash"}
MAX_HISTORIAL = 8


class BuscarView(VistaBase):
    TITULO = "Buscar valores"
    SUBTITULO = "Busca un número entero con el método que elijas."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        zona = ctk.CTkScrollableFrame(self, fg_color="transparent")
        zona.grid(row=0, column=0, sticky="nsew")
        zona.columnconfigure(0, weight=1)
        self._historial = []
        self._version = app.version_carga

        p = panel(zona, "Búsqueda")
        p.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        c = p.cuerpo
        etiqueta(c, "Método", 13, suave=True, anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=(0, 20))
        self.sel = ctk.CTkSegmentedButton(
            c, values=list(METODOS), command=self._cambio_metodo, font=fuente(13),
            selected_color=COLORES["primario"], selected_hover_color=COLORES["primario_hover"],
            unselected_color=COLORES["superficie_alt"], unselected_hover_color=COLORES["borde"])
        self.sel.set("Secuencial")
        self.sel.grid(row=0, column=1, sticky="w", pady=8)
        self.registrar(self.sel)

        etiqueta(c, "Valor", 13, suave=True, anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=(0, 20))
        fila = ctk.CTkFrame(c, fg_color="transparent")
        fila.grid(row=1, column=1, sticky="w", pady=8)
        self.entrada = ctk.CTkEntry(fila, placeholder_text="Número entero", width=220, height=36,
                                    font=fuente(13), fg_color=COLORES["fondo"],
                                    border_color=COLORES["borde"])
        self.entrada.pack(side="left", padx=(0, 12))
        self.entrada.bind("<Return>", lambda _e: self._buscar())
        self.btn = self.registrar(boton(fila, "Buscar", self._buscar, ancho=120))
        self.btn.pack(side="left")
        self.nota = etiqueta(c, "", 12, suave=True, anchor="w", justify="left", wraplength=760)
        self.nota.grid(row=2, column=0, columnspan=2, sticky="w")

        self.banner = Banner(zona)
        self.banner.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.banner.ocultar()

        fila = ctk.CTkFrame(zona, fg_color="transparent")
        fila.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        fila.columnconfigure((0, 1, 2, 3), weight=1, uniform="b")
        self.t_resultado = StatCard(fila, "Resultado", "—")
        self.t_posicion = StatCard(fila, "Posición", "—")
        self.t_tiempo = StatCard(fila, "Tiempo", "—")
        self.t_repeticiones = StatCard(fila, "Repeticiones", "—")
        for i, t in enumerate((self.t_resultado, self.t_posicion, self.t_tiempo, self.t_repeticiones)):
            t.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 3 else 7))

        ph = panel(zona, "Historial de búsquedas")
        ph.grid(row=3, column=0, sticky="ew")
        self.tabla = Tabla(ph.cuerpo, [("Método", 2, "w"), ("Valor", 2, "e"),
                                        ("Resultado", 3, "w"), ("Tiempo", 2, "e")])
        self.tabla.pack(fill="x")
        self.tabla.llenar([])
        self._cambio_metodo("Secuencial")

    # ------------------------------------------------------------------
    def _cambio_metodo(self, valor=None):
        metodo = self.sel.get()
        textos = {
            "Secuencial": "Recorre los datos uno por uno. Funciona con datos ordenados o no.",
            "Binaria": "Requiere datos ordenados (ascendente o descendente). Ordénalos primero.",
            "Hash": "Construye una tabla hash la primera vez y la reutiliza en las siguientes búsquedas.",
        }
        self.nota.configure(text=textos[metodo])

    def _buscar(self):
        if self.app.ocupado:
            self.app.notificar("Espera a que termine la operación en curso.", "aviso")
            return
        if not self.sesion.cargado:
            self.banner.mostrar("Primero carga un archivo en «Cargar archivo».", "aviso")
            return
        texto = self.entrada.get().strip()
        try:
            valor = int(texto)
        except ValueError:
            self.banner.mostrar("Escribe un número entero válido (por ejemplo 4521).", "error")
            return
        self.banner.ocultar()
        metodo = METODOS[self.sel.get()]
        try:
            r = self.sesion.buscar(metodo, valor)
        except ValueError as error:
            self.banner.mostrar(str(error), "error")
            return

        encontrado = r["posicion"] >= 0
        if encontrado:
            self.t_resultado.actualizar("Encontrado", f"el valor {valor} existe", "exito")
            self.t_posicion.actualizar(f"Índice {r['posicion']}",
                                       f"posición {r['posicion'] + 1} de {self.sesion.total:,}")
        else:
            self.t_resultado.actualizar("No encontrado", f"el valor {valor} no está", "error")
            self.t_posicion.actualizar("—", "")
        self.t_tiempo.actualizar(f"{r['segundos'] * 1e6:.2f} µs", f"{r['segundos']:.8f} s")
        if r["repeticiones"] is None:
            self.t_repeticiones.actualizar("—", "solo lo informa la búsqueda hash")
        else:
            self.t_repeticiones.actualizar(str(r["repeticiones"]), "veces que aparece el valor")
        if r["segundos_construccion"] is not None:
            self.banner.mostrar(f"Se construyó la tabla hash en {r['segundos_construccion']:.6f} s "
                                "(solo ocurre la primera vez).", "info")

        resumen = "Encontrado" if encontrado else "No encontrado"
        if encontrado:
            resumen += f" · índice {r['posicion']}"
        self._historial.insert(0, (self.sel.get(), str(valor), resumen, f"{r['segundos'] * 1e6:.2f} µs"))
        del self._historial[MAX_HISTORIAL:]
        self.tabla.llenar(self._historial)

    def al_mostrar(self):
        if self._version != self.app.version_carga:      # se cargó otro archivo
            self._version = self.app.version_carga
            self._historial = []
            self.tabla.llenar([])
            for t in (self.t_resultado, self.t_posicion, self.t_tiempo, self.t_repeticiones):
                t.actualizar("—", "")
        self.sel.configure(state=self.estado())
        self.entrada.configure(state="normal" if not self.app.ocupado else "disabled")
        self.btn.configure(state=self.estado(self.sesion.cargado))
        if not self.sesion.cargado:
            self.banner.mostrar("Aún no hay datos. Carga un archivo para poder buscar.", "info")
        elif self.banner._texto.cget("text").startswith("Aún no hay datos"):
            self.banner.ocultar()
