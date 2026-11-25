"""Ordenar los datos con un algoritmo interno o externo."""
import customtkinter as ctk

import backend
from frontend.components.cards import Banner, StatCard, boton, etiqueta, panel
from frontend.config import COLORES, fuente
from frontend.views import VistaBase


def mismos_valores(a, b):
    """True si ambas listas tienen exactamente los mismos valores, duplicados incluidos.
    Cuenta ocurrencias con un diccionario (no usa ordenamiento)."""
    if len(a) != len(b):
        return False
    cuenta = {}
    for x in a:
        cuenta[x] = cuenta.get(x, 0) + 1
    for x in b:
        restantes = cuenta.get(x, 0)
        if restantes == 0:
            return False
        cuenta[x] = restantes - 1
    return True


class OrdenarView(VistaBase):
    TITULO = "Ordenar datos"
    SUBTITULO = "Elige el tipo de ordenamiento, el algoritmo y el sentido."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.columnconfigure(0, weight=1)
        self._algoritmos = []

        cfg = panel(self, "Configuración")
        cfg.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        c = cfg.cuerpo
        c.columnconfigure(1, weight=1)

        estilo = dict(selected_color=COLORES["primario"], selected_hover_color=COLORES["primario_hover"],
                      unselected_color=COLORES["superficie_alt"],
                      unselected_hover_color=COLORES["borde"], font=fuente(13))

        etiqueta(c, "Tipo", 13, suave=True, anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=(0, 20))
        self.sel_tipo = ctk.CTkSegmentedButton(c, values=["Interno", "Externo"],
                                               command=self._cambio_tipo, **estilo)
        self.sel_tipo.set("Interno")
        self.sel_tipo.grid(row=0, column=1, sticky="w", pady=8)
        self.registrar(self.sel_tipo)

        etiqueta(c, "Algoritmo", 13, suave=True, anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=(0, 20))
        self.menu = ctk.CTkOptionMenu(c, values=["—"], width=320, height=34, font=fuente(13),
                                      dropdown_font=fuente(13), fg_color=COLORES["superficie_alt"],
                                      button_color=COLORES["primario"],
                                      button_hover_color=COLORES["primario_hover"])
        self.menu.grid(row=1, column=1, sticky="w", pady=8)
        self.registrar(self.menu)

        etiqueta(c, "Sentido", 13, suave=True, anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=(0, 20))
        self.sel_sentido = ctk.CTkSegmentedButton(c, values=["Ascendente", "Descendente"], **estilo)
        self.sel_sentido.set("Ascendente")
        self.sel_sentido.grid(row=2, column=1, sticky="w", pady=8)
        self.registrar(self.sel_sentido)

        self.nota = etiqueta(c, "", 12, suave=True, anchor="w", justify="left", wraplength=760)
        self.nota.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 10))
        self.btn = self.registrar(boton(c, "Ordenar datos", self._ordenar, ancho=190))
        self.btn.grid(row=4, column=0, columnspan=2, sticky="w")

        self.banner = Banner(self)
        self.banner.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.banner.ocultar()

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.grid(row=2, column=0, sticky="ew")
        fila.columnconfigure((0, 1, 2, 3), weight=1, uniform="r")
        self.t_algoritmo = StatCard(fila, "Algoritmo", "—", tam_valor=15)
        self.t_tiempo = StatCard(fila, "Tiempo", "—", tam_valor=17)
        self.t_pasadas = StatCard(fila, "Pasadas de mezcla", "—", tam_valor=17)
        self.t_verif = StatCard(fila, "Verificación", "—", tam_valor=17)
        for i, t in enumerate((self.t_algoritmo, self.t_tiempo, self.t_pasadas, self.t_verif)):
            t.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 3 else 7))

        self._cambio_tipo("Interno")

    # ------------------------------------------------------------------
    def _tipo_actual(self):
        return "interno" if self.sel_tipo.get() == "Interno" else "externo"

    def _cambio_tipo(self, _valor=None):
        tipo = self._tipo_actual()
        self._algoritmos = backend.algoritmos(tipo)
        nombres = [nombre for _clave, nombre in self._algoritmos]
        self.menu.configure(values=nombres)
        self.menu.set(nombres[0])
        if tipo == "interno":
            self.nota.configure(text="Los datos se ordenan en memoria. Burbuja, Selección e Inserción "
                                     "pueden tardar unos segundos con 5,000 registros.")
        else:
            self.nota.configure(text="Los datos se escriben en archivos auxiliares dentro de resultados/ "
                                     "y se mezclan archivo a archivo. Puede tardar varios segundos.")

    def _clave_actual(self):
        elegido = self.menu.get()
        for clave, nombre in self._algoritmos:
            if nombre == elegido:
                return clave
        return None

    def _ordenar(self):
        if not self.sesion.cargado:
            self.banner.mostrar("Primero carga un archivo en «Cargar archivo».", "aviso")
            return
        self.banner.ocultar()
        sesion = self.sesion
        tipo, clave = self._tipo_actual(), self._clave_actual()
        ascendente = self.sel_sentido.get() == "Ascendente"

        def tarea():
            r = sesion.ordenar(tipo, clave, ascendente)
            return r, mismos_valores(sesion.original, r["datos"])

        def listo(salida):
            r, conserva = salida
            self.t_algoritmo.actualizar(r["algoritmo"], f"{r['tipo']} · {'ascendente' if r['ascendente'] else 'descendente'}")
            self.t_tiempo.actualizar(f"{r['segundos']:.6f} s", f"{r['segundos'] * 1000:.3f} ms")
            self.t_pasadas.actualizar("—" if r["pasadas"] is None else str(r["pasadas"]),
                                      "solo ordenamiento externo")
            if r["correcto"] and conserva:
                self.t_verif.actualizar("Correcta", "orden y valores íntegros", "exito")
                self.banner.mostrar(f"Datos ordenados con {r['algoritmo']} en {r['segundos']:.6f} s.", "exito")
                self.app.notificar(f"Ordenado con {r['algoritmo']}.", "exito")
            else:
                self.t_verif.actualizar("FALLÓ", "el resultado no coincide con los datos originales", "error")
                self.banner.mostrar("La verificación falló: el resultado no está bien ordenado o "
                                    "cambió algún valor.", "error")
            self.app.actualizar_estado()

        mensaje = "Ordenando con archivos auxiliares…" if tipo == "externo" else "Ordenando en memoria…"
        self.app.ejecutar_tarea(tarea, listo, mensaje, lambda texto: self.banner.mostrar(texto, "error"))

    def al_mostrar(self):
        self.btn.configure(state=self.estado(self.sesion.cargado))
        for w in (self.sel_tipo, self.menu, self.sel_sentido):
            w.configure(state=self.estado())
        if not self.sesion.cargado:
            self.banner.mostrar("Aún no hay datos. Carga un archivo para poder ordenar.", "info")
        elif self.banner._texto.cget("text").startswith("Aún no hay datos"):
            self.banner.ocultar()
