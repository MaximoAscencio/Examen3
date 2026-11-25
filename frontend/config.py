"""Colores, dimensiones y tipografías de DATAFLOW."""

COLORES = {
    "fondo": "#111318",
    "sidebar": "#181B23",
    "superficie": "#20242E",
    "superficie_alt": "#2A2F3B",
    "fila_alt": "#252A36",
    "borde": "#343A48",
    "primario": "#6366F1",
    "primario_hover": "#4F46E5",
    "texto": "#E5E7EB",
    "texto_suave": "#9CA3AF",
    "exito": "#22C55E",
    "error": "#EF4444",
    "aviso": "#F59E0B",
    "info": "#38BDF8",
}

TIPOGRAFIA = "Segoe UI"

VENTANA_ANCHO = 1240
VENTANA_ALTO = 780
VENTANA_MIN_ANCHO = 1080
VENTANA_MIN_ALTO = 700
ANCHO_SIDEBAR = 240
RADIO = 12
PAD = 24

# (clave, texto del menú) en el orden en que se muestran
SECCIONES = [
    ("inicio", "Inicio"),
    ("cargar", "Cargar archivo"),
    ("ordenar", "Ordenar datos"),
    ("buscar", "Buscar valores"),
    ("resultados", "Resultados"),
    ("exportar", "Exportar"),
    ("comparar", "Comparar algoritmos"),
]


def fuente(tamano=13, peso="normal"):
    """Tupla de fuente lista para cualquier widget de CustomTkinter."""
    return (TIPOGRAFIA, tamano, peso)
