"""Encabezado: título de la sección y estado de la sesión."""
import customtkinter as ctk

from frontend.config import COLORES, PAD, fuente


class Header(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", height=88)
        self.columnconfigure(0, weight=1)
        self.grid_propagate(False)

        izquierda = ctk.CTkFrame(self, fg_color="transparent")
        izquierda.grid(row=0, column=0, sticky="w", padx=PAD, pady=(18, 0))
        self._titulo = ctk.CTkLabel(izquierda, text="", font=fuente(24, "bold"),
                                    text_color=COLORES["texto"], anchor="w")
        self._titulo.pack(anchor="w")
        self._subtitulo = ctk.CTkLabel(izquierda, text="", font=fuente(13),
                                       text_color=COLORES["texto_suave"], anchor="w")
        self._subtitulo.pack(anchor="w")

        chip = ctk.CTkFrame(self, fg_color=COLORES["superficie"], corner_radius=18)
        chip.grid(row=0, column=1, sticky="e", padx=PAD, pady=(18, 0))
        self._punto = ctk.CTkLabel(chip, text="●", font=fuente(12),
                                   text_color=COLORES["texto_suave"])
        self._punto.pack(side="left", padx=(14, 6), pady=7)
        self._estado = ctk.CTkLabel(chip, text="Sin archivo cargado", font=fuente(12),
                                    text_color=COLORES["texto"])
        self._estado.pack(side="left", padx=(0, 14), pady=7)

    def poner_titulo(self, titulo, subtitulo=""):
        self._titulo.configure(text=titulo)
        self._subtitulo.configure(text=subtitulo)

    def poner_estado(self, texto, color):
        self._punto.configure(text_color=color)
        self._estado.configure(text=texto)
