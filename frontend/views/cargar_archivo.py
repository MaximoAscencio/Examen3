"""Cargar un archivo TXT o XLSX."""
import os
from tkinter import filedialog

import customtkinter as ctk

import backend
from frontend.components.cards import Banner, StatCard, boton, etiqueta, panel
from frontend.views import VistaBase


class CargarArchivoView(VistaBase):
    TITULO = "Cargar archivo"
    SUBTITULO = "Selecciona un archivo TXT o XLSX con números enteros."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.columnconfigure(0, weight=1)
        self._invalidas = 0
        self._botones_lista = []

        p1 = panel(self, "Seleccionar archivo")
        p1.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        etiqueta(p1.cuerpo, "Elige un archivo de tu equipo. Los valores que no sean "
                 "enteros se ignoran y se te avisa cuántos fueron.", 12, suave=True,
                 anchor="w", justify="left", wraplength=780).pack(fill="x", pady=(0, 10))
        self.btn_examinar = self.registrar(
            boton(p1.cuerpo, "Examinar…", self._examinar, ancho=170))
        self.btn_examinar.pack(anchor="w")

        self.banner = Banner(self)
        self.banner.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.banner.ocultar()

        p2 = panel(self, "Archivos de la carpeta datos/")
        p2.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        self.lista = ctk.CTkFrame(p2.cuerpo, fg_color="transparent")
        self.lista.pack(fill="x")
        self.btn_actualizar = self.registrar(
            boton(p2.cuerpo, "Actualizar lista", self._poblar_lista, "secundario", ancho=150))
        self.btn_actualizar.pack(anchor="w", pady=(8, 0))

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.grid(row=3, column=0, sticky="ew")
        fila.columnconfigure((0, 1, 2), weight=1, uniform="c")
        self.t_archivo = StatCard(fila, "Archivo actual", "Ninguno", tam_valor=14)
        self.t_registros = StatCard(fila, "Registros válidos", "0")
        self.t_ignorados = StatCard(fila, "Valores ignorados", "0")
        self.t_archivo.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self.t_registros.grid(row=0, column=1, sticky="nsew", padx=7)
        self.t_ignorados.grid(row=0, column=2, sticky="nsew", padx=(7, 0))
        self._poblar_lista()

    # ------------------------------------------------------------------
    def _poblar_lista(self):
        for b in self._botones_lista:
            if b in self._acciones:
                self._acciones.remove(b)
            b.destroy()
        self._botones_lista = []
        nombres = backend.listar_archivos_datos()
        if not nombres:
            etiqueta(self.lista, "No hay archivos .txt o .xlsx en datos/.", 12, suave=True,
                     anchor="w").pack(fill="x")
            self._botones_lista.append(self.lista.winfo_children()[-1])
            return
        for nombre in nombres:
            ruta = os.path.join(backend.CARPETA_DATOS, nombre)
            b = boton(self.lista, nombre, lambda r=ruta: self._cargar(r), "secundario",
                      anchor="w", state=self.estado())
            b.pack(fill="x", pady=3)
            self._botones_lista.append(b)
            self._acciones.append(b)

    def _examinar(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un archivo de datos",
            initialdir=backend.CARPETA_DATOS if os.path.isdir(backend.CARPETA_DATOS) else None,
            filetypes=[("Archivos de datos", "*.txt *.xlsx"), ("TXT", "*.txt"),
                       ("XLSX", "*.xlsx"), ("Todos", "*.*")])
        if ruta:
            self._cargar(ruta)

    def _cargar(self, ruta):
        self.banner.ocultar()
        sesion = self.sesion

        def tarea():
            return sesion.cargar(ruta)

        def listo(invalidas):
            self._invalidas = invalidas
            self.app.version_carga += 1
            texto = f"Se cargó {sesion.nombre_archivo} con {sesion.total:,} registros."
            if invalidas:
                texto += f" Se ignoraron {invalidas:,} valor(es) que no eran enteros."
            tono = "aviso" if invalidas else "exito"
            self.banner.mostrar(texto, tono)
            self.app.notificar(texto, tono)
            self.app.actualizar_estado()

        def fallo(texto):
            self.banner.mostrar(texto, "error")

        self.app.ejecutar_tarea(tarea, listo, f"Cargando {os.path.basename(ruta)}…", fallo)

    def al_mostrar(self):
        for b in self._botones_lista:
            if isinstance(b, ctk.CTkButton):
                b.configure(state=self.estado())
        self.btn_examinar.configure(state=self.estado())
        self.btn_actualizar.configure(state=self.estado())
        s = self.sesion
        if s.cargado:
            self.t_archivo.actualizar(s.nombre_archivo)
            self.t_registros.actualizar(f"{s.total:,}")
            self.t_ignorados.actualizar(f"{self._invalidas:,}", tono="aviso" if self._invalidas else None)
        else:
            self.t_archivo.actualizar("Ninguno")
            self.t_registros.actualizar("0")
            self.t_ignorados.actualizar("0")
