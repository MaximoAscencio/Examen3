"""Pantalla de inicio: resumen de la sesión y accesos rápidos."""
import customtkinter as ctk

from frontend.components.cards import StatCard, boton, etiqueta, panel
from frontend.config import COLORES
from frontend.views import VistaBase


class DashboardView(VistaBase):
    TITULO = "Inicio"
    SUBTITULO = "Resumen de tu sesión de trabajo."

    def __init__(self, master, app):
        super().__init__(master, app)
        self.columnconfigure((0, 1, 2, 3), weight=1, uniform="tarjetas")

        self.t_archivo = StatCard(self, "Archivo", "Sin cargar", tam_valor=15)
        self.t_registros = StatCard(self, "Registros", "0")
        self.t_estado = StatCard(self, "Estado de los datos", "Sin datos", tam_valor=17)
        self.t_tiempo = StatCard(self, "Último ordenamiento", "—", tam_valor=17)
        for i, tarjeta in enumerate((self.t_archivo, self.t_registros,
                                     self.t_estado, self.t_tiempo)):
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 3 else 7),
                         pady=(0, 14))

        pasos = panel(self, "Flujo de trabajo")
        pasos.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 7), pady=(0, 14))
        self._pasos = []
        for texto in ("Cargar un archivo TXT o XLSX",
                      "Ordenar con un algoritmo interno o externo",
                      "Buscar valores (secuencial, binaria o hash)",
                      "Exportar los datos y el reporte"):
            fila = etiqueta(pasos.cuerpo, "", 13, anchor="w")
            fila.pack(fill="x", pady=4)
            self._pasos.append((fila, texto))

        acciones = panel(self, "Accesos rápidos")
        acciones.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=(7, 0), pady=(0, 14))
        for clave, texto in (("cargar", "Cargar archivo"), ("ordenar", "Ordenar datos"),
                             ("buscar", "Buscar valores"), ("comparar", "Comparar algoritmos")):
            boton(acciones.cuerpo, texto, lambda c=clave: self.app.mostrar(c),
                  estilo="secundario").pack(fill="x", pady=4)
        self.rowconfigure(1, weight=1)

    def al_mostrar(self):
        s = self.sesion
        if not s.cargado:
            self.t_archivo.actualizar("Sin cargar", "Carga un archivo para comenzar")
            self.t_registros.actualizar("0", "")
            self.t_estado.actualizar("Sin datos", "")
            self.t_tiempo.actualizar("—", "")
        else:
            self.t_archivo.actualizar(s.nombre_archivo, "")
            self.t_registros.actualizar(f"{s.total:,}", "números enteros")
            if s.ordenado:
                u = s.ultimo
                self.t_estado.actualizar("Ordenados", "ascendente" if u["ascendente"] else "descendente",
                                         "exito")
                self.t_tiempo.actualizar(f"{u['segundos']:.6f} s", u["algoritmo"])
            else:
                self.t_estado.actualizar("Originales", "sin ordenar", "aviso")
                self.t_tiempo.actualizar("—", "aún no se ordena")
        hechos = (s.cargado, s.ordenado, s.cargado, s.cargado)
        for (fila, texto), hecho in zip(self._pasos, hechos):
            marca = "✔" if hecho else "○"
            fila.configure(text=f"{marca}   {texto}",
                           text_color=COLORES["exito"] if hecho else COLORES["texto_suave"])
