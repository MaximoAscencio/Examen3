"""Vistas de DATAFLOW. VistaBase define lo que toda pantalla comparte."""
import customtkinter as ctk


class VistaBase(ctk.CTkFrame):
    TITULO = ""
    SUBTITULO = ""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.sesion = app.sesion          # la MISMA instancia de Sesion para todas las vistas
        self._acciones = []               # botones que se bloquean durante una tarea larga

    def registrar(self, widget):
        self._acciones.append(widget)
        return widget

    def estado(self, condicion=True):
        """'normal' solo si se cumple la condición y no hay una tarea en curso."""
        return "normal" if condicion and not self.app.ocupado else "disabled"

    def al_mostrar(self):
        """Se llama cada vez que la vista aparece o cambia el estado de la sesión."""

    def set_ocupado(self, ocupado):
        if ocupado:
            for widget in self._acciones:
                widget.configure(state="disabled")
        else:
            self.al_mostrar()
