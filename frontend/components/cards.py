"""Componentes reutilizables: tarjetas, paneles, botones, avisos, toast y tablas."""
import customtkinter as ctk

from frontend.config import COLORES, RADIO, fuente

# tono -> (color del texto/acento, color de fondo)
TONOS = {
    "exito": (COLORES["exito"], "#12301D"),
    "error": (COLORES["error"], "#381416"),
    "aviso": (COLORES["aviso"], "#382B0F"),
    "info": (COLORES["info"], "#10283A"),
}


def boton(master, texto, comando, estilo="primario", ancho=None, **extra):
    """Botón con el estilo de DATAFLOW. estilo: 'primario' o 'secundario'."""
    if estilo == "primario":
        fondo, hover, color = COLORES["primario"], COLORES["primario_hover"], "#FFFFFF"
    else:
        fondo, hover, color = COLORES["superficie_alt"], COLORES["borde"], COLORES["texto"]
    if ancho:
        extra["width"] = ancho
    return ctk.CTkButton(master, text=texto, command=comando, fg_color=fondo,
                         hover_color=hover, text_color=color,
                         text_color_disabled=COLORES["texto_suave"], height=38,
                         corner_radius=8, font=fuente(13, "bold"), **extra)


def etiqueta(master, texto, tam=13, peso="normal", suave=False, **extra):
    return ctk.CTkLabel(master, text=texto, font=fuente(tam, peso),
                        text_color=COLORES["texto_suave"] if suave else COLORES["texto"],
                        **extra)


def panel(master, titulo=None):
    """Superficie con título opcional. Los widgets van dentro de panel.cuerpo."""
    marco = ctk.CTkFrame(master, fg_color=COLORES["superficie"], corner_radius=RADIO)
    if titulo:
        ctk.CTkLabel(marco, text=titulo, font=fuente(15, "bold"),
                     text_color=COLORES["texto"], anchor="w"
                     ).pack(fill="x", padx=18, pady=(14, 0))
    marco.cuerpo = ctk.CTkFrame(marco, fg_color="transparent")
    marco.cuerpo.pack(fill="both", expand=True, padx=18, pady=(8, 16))
    return marco


class StatCard(ctk.CTkFrame):
    """Tarjeta estadística: título pequeño, valor grande y detalle."""

    def __init__(self, master, titulo, valor="—", detalle="", tam_valor=20):
        super().__init__(master, fg_color=COLORES["superficie"], corner_radius=RADIO)
        self.columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=titulo.upper(), font=fuente(10, "bold"),
                     text_color=COLORES["texto_suave"], anchor="w"
                     ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        self._valor = ctk.CTkLabel(self, text=valor, font=fuente(tam_valor, "bold"),
                                   text_color=COLORES["texto"], anchor="w")
        self._valor.grid(row=1, column=0, sticky="ew", padx=16, pady=(2, 0))
        self._detalle = ctk.CTkLabel(self, text=detalle, font=fuente(11),
                                     text_color=COLORES["texto_suave"], anchor="w")
        self._detalle.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

    def actualizar(self, valor=None, detalle=None, tono=None):
        if valor is not None:
            self._valor.configure(text=valor)
        if detalle is not None:
            self._detalle.configure(text=detalle)
        color = TONOS[tono][0] if tono else COLORES["texto"]
        self._valor.configure(text_color=color)


class Banner(ctk.CTkFrame):
    """Mensaje dentro de una vista. El que lo usa lo coloca con grid()."""

    def __init__(self, master):
        super().__init__(master, corner_radius=10, border_width=1)
        self._texto = ctk.CTkLabel(self, text="", font=fuente(13), anchor="w",
                                   justify="left", wraplength=800)
        self._texto.pack(fill="x", padx=16, pady=11)

    def mostrar(self, texto, tono="info"):
        acento, fondo = TONOS[tono]
        self.configure(fg_color=fondo, border_color=acento)
        self._texto.configure(text=texto, text_color=acento)
        self.grid()

    def ocultar(self):
        self.grid_remove()


class Toast(ctk.CTkFrame):
    """Notificación flotante que desaparece sola."""

    def __init__(self, master):
        super().__init__(master, corner_radius=10, border_width=1)
        self._texto = ctk.CTkLabel(self, text="", font=fuente(13), justify="left",
                                   wraplength=420)
        self._texto.pack(padx=18, pady=12)
        self._pendiente = None

    def mostrar(self, texto, tono="info", ms=4500):
        acento, fondo = TONOS[tono]
        self.configure(fg_color=fondo, border_color=acento)
        self._texto.configure(text=texto, text_color=acento)
        self.place(relx=1.0, rely=1.0, x=-24, y=-56, anchor="se")
        self.tkraise()
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(ms, self.ocultar)

    def ocultar(self):
        self._pendiente = None
        self.place_forget()


class Tabla(ctk.CTkFrame):
    """Tabla simple de solo lectura.

    columnas: lista de (título, peso, alineación) con alineación 'w', 'e' o 'center'.
    barra=True agrega al final una columna con barras de progreso.
    """

    def __init__(self, master, columnas, alto_fila=26, barra=False):
        super().__init__(master, fg_color="transparent")
        self.columnas = columnas
        self.alto_fila = alto_fila
        self.barra = barra
        self._celdas = []
        for j, (titulo, peso, _alin) in enumerate(columnas):
            self.columnconfigure(j, weight=peso)
        if barra:
            self.columnconfigure(len(columnas), weight=4)
        for j, (titulo, _peso, alin) in enumerate(columnas):
            self._celda(titulo, 0, j, COLORES["superficie_alt"], COLORES["texto_suave"],
                        alin, fuente(11, "bold"), guardar=False)
        if barra:
            self._celda("PROPORCIÓN", 0, len(columnas), COLORES["superficie_alt"],
                        COLORES["texto_suave"], "w", fuente(11, "bold"), guardar=False)

    def _celda(self, texto, fila, col, fondo, color, alin, fnt, guardar=True, span=1):
        pre = "  " if alin in ("w", "center") else ""
        post = "  " if alin == "e" else ""
        etiqueta_ = ctk.CTkLabel(self, text=f"{pre}{texto}{post}", anchor=alin,
                                 fg_color=fondo, text_color=color, font=fnt,
                                 height=self.alto_fila, corner_radius=0)
        etiqueta_.grid(row=fila, column=col, columnspan=span, sticky="nsew")
        if guardar:
            self._celdas.append(etiqueta_)
        return etiqueta_

    def llenar(self, filas, resaltar=None, barras=None):
        for w in self._celdas:
            w.destroy()
        self._celdas = []
        total_cols = len(self.columnas) + (1 if self.barra else 0)
        if not filas:
            self._celda("Sin datos", 1, 0, COLORES["superficie"], COLORES["texto_suave"],
                        "center", fuente(12), span=total_cols)
            return
        for i, fila in enumerate(filas):
            fondo = COLORES["superficie"] if i % 2 == 0 else COLORES["fila_alt"]
            color = COLORES["exito"] if i == resaltar else COLORES["texto"]
            peso = "bold" if i == resaltar else "normal"
            for j, valor in enumerate(fila):
                self._celda(valor, i + 1, j, fondo, color, self.columnas[j][2],
                            fuente(12, peso))
            if self.barra:
                soporte = ctk.CTkFrame(self, fg_color=fondo, corner_radius=0,
                                       height=self.alto_fila)
                soporte.grid(row=i + 1, column=len(self.columnas), sticky="nsew")
                barra = ctk.CTkProgressBar(
                    soporte, height=8, corner_radius=4, fg_color=COLORES["superficie_alt"],
                    progress_color=COLORES["exito"] if i == resaltar else COLORES["primario"])
                barra.set(barras[i] if barras else 0)
                barra.pack(fill="x", padx=10, pady=8)
                self._celdas.append(soporte)
