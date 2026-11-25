"""Menú lateral de navegación."""
import customtkinter as ctk

from frontend.config import ANCHO_SIDEBAR, COLORES, fuente


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, secciones, al_seleccionar):
        super().__init__(master, width=ANCHO_SIDEBAR, corner_radius=0,
                         fg_color=COLORES["sidebar"])
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(len(secciones) + 2, weight=1)   # espacio flexible
        self._botones = {}

        ctk.CTkLabel(self, text="DATAFLOW", font=fuente(22, "bold"),
                     text_color=COLORES["texto"], anchor="w"
                     ).grid(row=0, column=0, sticky="ew", padx=22, pady=(26, 0))
        ctk.CTkLabel(self, text="Ordenamiento y búsqueda", font=fuente(11),
                     text_color=COLORES["texto_suave"], anchor="w"
                     ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 22))

        for i, (clave, texto) in enumerate(secciones):
            boton = ctk.CTkButton(
                self, text=f"  {i + 1}    {texto}", anchor="w", height=42,
                corner_radius=8, fg_color="transparent",
                hover_color=COLORES["superficie"], text_color=COLORES["texto_suave"],
                font=fuente(13), command=lambda c=clave: al_seleccionar(c))
            boton.grid(row=i + 2, column=0, sticky="ew", padx=12, pady=2)
            self._botones[clave] = boton

        self._pie = ctk.CTkLabel(self, text="Sin archivo", font=fuente(11),
                                 text_color=COLORES["texto_suave"], anchor="w",
                                 justify="left", wraplength=ANCHO_SIDEBAR - 44)
        self._pie.grid(row=len(secciones) + 3, column=0, sticky="ew",
                       padx=22, pady=(8, 22))

    def activar(self, clave):
        for k, boton in self._botones.items():
            if k == clave:
                boton.configure(fg_color=COLORES["primario"], hover_color=COLORES["primario_hover"],
                                text_color="#FFFFFF", font=fuente(13, "bold"))
            else:
                boton.configure(fg_color="transparent", hover_color=COLORES["superficie"],
                                text_color=COLORES["texto_suave"], font=fuente(13))

    def poner_pie(self, texto):
        self._pie.configure(text=texto)
