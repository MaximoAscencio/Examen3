"""Exportar los datos actuales y su reporte."""
import os
import subprocess
import sys

import customtkinter as ctk

import backend
from frontend.components.cards import Banner, boton, etiqueta, panel
from frontend.config import COLORES, fuente
from frontend.views import VistaBase


def abrir_carpeta(ruta):
    """Abre la carpeta en el explorador del sistema."""
    if hasattr(os, "startfile"):                 # Windows
        os.startfile(ruta)
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", ruta])


class ExportarView(VistaBase):
    TITULO = "Exportar"
    SUBTITULO = "Guarda los datos actuales y un reporte en la carpeta resultados/."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.columnconfigure(0, weight=1)

        p = panel(self, "Opciones de exportación")
        p.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        c = p.cuerpo
        etiqueta(c, "Formato", 13, suave=True, anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=(0, 20))
        self.sel = ctk.CTkSegmentedButton(
            c, values=["TXT", "XLSX"], font=fuente(13),
            selected_color=COLORES["primario"], selected_hover_color=COLORES["primario_hover"],
            unselected_color=COLORES["superficie_alt"], unselected_hover_color=COLORES["borde"])
        self.sel.set("TXT")
        self.sel.grid(row=0, column=1, sticky="w", pady=8)
        self.registrar(self.sel)

        etiqueta(c, "Nombre", 13, suave=True, anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=(0, 20))
        self.entrada = ctk.CTkEntry(c, width=300, height=36, font=fuente(13),
                                    fg_color=COLORES["fondo"], border_color=COLORES["borde"])
        self.entrada.insert(0, "datos_ordenados")
        self.entrada.grid(row=1, column=1, sticky="w", pady=8)
        self.registrar(self.entrada)

        self.nota = etiqueta(c, "", 12, suave=True, anchor="w", justify="left", wraplength=760)
        self.nota.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 10))
        botones = ctk.CTkFrame(c, fg_color="transparent")
        botones.grid(row=3, column=0, columnspan=2, sticky="w")
        self.btn = self.registrar(boton(botones, "Exportar", self._exportar, ancho=160))
        self.btn.pack(side="left", padx=(0, 12))
        boton(botones, "Abrir carpeta resultados", self._abrir, "secundario", ancho=220
              ).pack(side="left")

        self.banner = Banner(self)
        self.banner.grid(row=1, column=0, sticky="ew")
        self.banner.ocultar()

    def _abrir(self):
        try:
            os.makedirs(backend.CARPETA_RESULTADOS, exist_ok=True)
            abrir_carpeta(backend.CARPETA_RESULTADOS)
        except OSError as error:
            self.banner.mostrar(f"No se pudo abrir la carpeta: {error}", "error")

    def _exportar(self):
        if not self.sesion.cargado:
            self.banner.mostrar("Primero carga un archivo en «Cargar archivo».", "aviso")
            return
        nombre = self.entrada.get().strip() or "datos_ordenados"
        formato = self.sel.get().lower()
        sesion = self.sesion

        def tarea():
            return sesion.exportar(formato, nombre)

        def listo(rutas):
            datos, reporte = rutas
            texto = (f"Exportación completa.\nDatos: {datos}\nReporte: {reporte}")
            self.banner.mostrar(texto, "exito")
            self.app.notificar("Archivos exportados en resultados/.", "exito")

        self.app.ejecutar_tarea(tarea, listo, "Exportando…",
                                lambda texto: self.banner.mostrar(texto, "error"))

    def al_mostrar(self):
        self.btn.configure(state=self.estado(self.sesion.cargado))
        self.sel.configure(state=self.estado())
        self.entrada.configure(state=self.estado())
        if not self.sesion.cargado:
            self.nota.configure(text="Aún no hay datos. Carga un archivo para poder exportar.")
        elif self.sesion.ordenado:
            self.nota.configure(text="Se guardarán los datos ordenados y un reporte con el algoritmo y el tiempo.")
        else:
            self.nota.configure(text="Los datos todavía no se han ordenado: se exportarán tal como se cargaron.")
