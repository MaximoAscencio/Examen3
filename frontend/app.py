"""DATAFLOW - ventana principal.

Ejecutar desde la carpeta del proyecto:
    python -m frontend.app
"""
import os
import queue
import sys
import threading
from tkinter import messagebox

# Permite también "python frontend/app.py": agrega la raíz del proyecto al path.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import customtkinter as ctk

from backend import Sesion
from frontend.components.cards import Toast
from frontend.components.header import Header
from frontend.components.sidebar import Sidebar
from frontend.config import (ANCHO_SIDEBAR, COLORES, PAD, SECCIONES, VENTANA_ALTO,
                             VENTANA_ANCHO, VENTANA_MIN_ALTO, VENTANA_MIN_ANCHO, fuente)
from frontend.views.buscar import BuscarView
from frontend.views.cargar_archivo import CargarArchivoView
from frontend.views.comparar import CompararView
from frontend.views.dashboard import DashboardView
from frontend.views.exportar import ExportarView
from frontend.views.ordenar import OrdenarView
from frontend.views.resultados import ResultadosView

VISTAS = {
    "inicio": DashboardView,
    "cargar": CargarArchivoView,
    "ordenar": OrdenarView,
    "buscar": BuscarView,
    "resultados": ResultadosView,
    "exportar": ExportarView,
    "comparar": CompararView,
}


def texto_de_error(error):
    """Mensaje en español listo para mostrar al usuario."""
    if isinstance(error, PermissionError):
        return ("No se pudo acceder al archivo: puede estar abierto en otro programa "
                "o no tienes permisos.")
    if isinstance(error, (ValueError, OSError)):
        return str(error)
    return f"Error inesperado ({type(error).__name__}): {error}"


class DataflowApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("DATAFLOW - Procesamiento y ordenamiento de datos")
        self.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}")
        self.minsize(VENTANA_MIN_ANCHO, VENTANA_MIN_ALTO)
        self.configure(fg_color=COLORES["fondo"])

        # Una única sesión compartida por todas las pantallas.
        self.sesion = Sesion()
        self.ocupado = False
        self.version_carga = 0        # sube cada vez que se carga un archivo nuevo
        self._cola = queue.Queue()
        self.vista_actual = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, SECCIONES, self.mostrar)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        principal = ctk.CTkFrame(self, fg_color="transparent")
        principal.grid(row=0, column=1, sticky="nsew")
        principal.columnconfigure(0, weight=1)
        principal.rowconfigure(1, weight=1)

        self.header = Header(principal)
        self.header.grid(row=0, column=0, sticky="ew")
        self.contenedor = ctk.CTkFrame(principal, fg_color="transparent")
        self.contenedor.grid(row=1, column=0, sticky="nsew", padx=PAD, pady=(8, 8))
        self.contenedor.columnconfigure(0, weight=1)
        self.contenedor.rowconfigure(0, weight=1)

        barra = ctk.CTkFrame(principal, fg_color=COLORES["sidebar"], corner_radius=0, height=34)
        barra.grid(row=2, column=0, sticky="ew")
        barra.columnconfigure(0, weight=1)
        barra.grid_propagate(False)
        self._estado = ctk.CTkLabel(barra, text="Listo", font=fuente(12),
                                    text_color=COLORES["texto_suave"], anchor="w")
        self._estado.grid(row=0, column=0, sticky="w", padx=PAD, pady=6)
        self._progreso = ctk.CTkProgressBar(barra, mode="indeterminate", width=180, height=6,
                                            progress_color=COLORES["primario"],
                                            fg_color=COLORES["superficie_alt"])
        self._progreso.grid(row=0, column=1, sticky="e", padx=PAD)
        self._progreso.grid_remove()

        self.vistas = {}
        for clave, clase in VISTAS.items():
            vista = clase(self.contenedor, self)
            vista.grid(row=0, column=0, sticky="nsew")
            self.vistas[clave] = vista

        self.toast = Toast(self)
        self.mostrar("inicio")
        self.actualizar_estado()
        self.after(80, self._procesar_cola)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ------------------------------------------------------------------
    # Navegación y estado
    # ------------------------------------------------------------------
    def mostrar(self, clave):
        vista = self.vistas[clave]
        self.vista_actual = clave
        self.sidebar.activar(clave)
        self.header.poner_titulo(vista.TITULO, vista.SUBTITULO)
        vista.tkraise()
        vista.al_mostrar()

    def actualizar_estado(self):
        s = self.sesion
        if not s.cargado:
            self.header.poner_estado("Sin archivo cargado", COLORES["texto_suave"])
            self.sidebar.poner_pie("Sin archivo cargado")
        elif s.ordenado:
            u = s.ultimo
            sentido = "asc" if u["ascendente"] else "desc"
            self.header.poner_estado(f"{s.nombre_archivo} · {s.total:,} registros · "
                                     f"{u['algoritmo']} ({sentido})", COLORES["exito"])
            self.sidebar.poner_pie(f"{s.nombre_archivo}\n{s.total:,} registros · ordenado")
        else:
            self.header.poner_estado(f"{s.nombre_archivo} · {s.total:,} registros · sin ordenar",
                                     COLORES["aviso"])
            self.sidebar.poner_pie(f"{s.nombre_archivo}\n{s.total:,} registros · sin ordenar")
        if self.vista_actual:
            self.vistas[self.vista_actual].al_mostrar()

    def notificar(self, texto, tono="info"):
        self.toast.mostrar(texto, tono)

    # ------------------------------------------------------------------
    # Tareas en segundo plano
    # ------------------------------------------------------------------
    def ejecutar_tarea(self, funcion, al_terminar, mensaje="Procesando…", al_fallar=None):
        """Ejecuta 'funcion' en un hilo. Los callbacks se ejecutan en el hilo principal.

        Solo se permite una tarea a la vez. Regresa False si ya hay una en curso."""
        if self.ocupado:
            self.notificar("Espera a que termine la operación en curso.", "aviso")
            return False
        self._poner_ocupado(True, mensaje)

        def trabajo():
            try:
                self._cola.put((True, funcion(), al_terminar, al_fallar))
            except Exception as error:                        # se informa en la interfaz
                self._cola.put((False, error, al_terminar, al_fallar))

        threading.Thread(target=trabajo, daemon=True).start()
        return True

    def _poner_ocupado(self, ocupado, mensaje="Listo"):
        self.ocupado = ocupado
        self._estado.configure(text=mensaje if ocupado else "Listo",
                               text_color=COLORES["info"] if ocupado else COLORES["texto_suave"])
        if ocupado:
            self._progreso.grid()
            self._progreso.start()
        else:
            self._progreso.stop()
            self._progreso.grid_remove()
        for vista in self.vistas.values():
            vista.set_ocupado(ocupado)

    def _procesar_cola(self):
        """Corre en el hilo principal: entrega los resultados de los hilos de trabajo."""
        try:
            while True:
                bien, valor, al_terminar, al_fallar = self._cola.get_nowait()
                self._poner_ocupado(False)
                try:
                    if bien:
                        al_terminar(valor)
                    else:
                        texto = texto_de_error(valor)
                        self.notificar(texto, "error")
                        if al_fallar:
                            al_fallar(texto)
                except Exception as error:
                    self.notificar(f"Error al mostrar el resultado: {error}", "error")
        except queue.Empty:
            pass
        self.after(80, self._procesar_cola)

    def _cerrar(self):
        if self.ocupado and not messagebox.askyesno(
                "Operación en curso", "Hay una operación en curso. ¿Cerrar de todos modos?"):
            return
        self.destroy()


def main():
    app = DataflowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
