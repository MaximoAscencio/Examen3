"""
auditoria.py - Auditoría técnica de DATAFLOW (Examen3)

Colócalo en la raíz del proyecto (junto a backend.py) y ejecuta:
    python auditoria.py

No modifica ningún archivo. Solo lee y reporta.
Copia TODA la salida y pégala en el chat.
"""
import ast
import importlib
import importlib.util
import inspect
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
IGNORAR = {".git", "__pycache__", ".venv", "venv", "env", "node_modules", ".idea", ".vscode"}
PROHIBIDOS_NOMBRE = {"sorted"}
PROHIBIDOS_ATTR = {"sort", "sort_values", "sort_index", "nsmallest", "nlargest"}
PROHIBIDOS_MODULO = {"heapq", "bisect", "numpy", "np"}

problemas = []


def titulo(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)


def ok(msg):
    print("  [OK]    " + msg)


def aviso(msg):
    print("  [AVISO] " + msg)
    problemas.append(msg)


def error(msg):
    print("  [ERROR] " + msg)
    problemas.append(msg)


def archivos_py():
    for base, dirs, files in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in IGNORAR]
        for f in files:
            if f.endswith(".py") and f != "auditoria.py":
                yield os.path.join(base, f)


def rel(p):
    return os.path.relpath(p, RAIZ)


def parsear(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as fh:
            return ast.parse(fh.read(), filename=ruta)
    except SyntaxError as e:
        error(f"Sintaxis inválida en {rel(ruta)} línea {e.lineno}: {e.msg}")
    except Exception as e:
        error(f"No se pudo leer {rel(ruta)}: {e}")
    return None


# ------------------------------------------------------------------ 1
def estructura():
    titulo("1. ESTRUCTURA DE ARCHIVOS")
    esperados = [
        "backend.py", "archivos.py", "busquedas.py", "ordenamientos_internos.py",
        "ordenamientos_externos.py", "main.py", "pruebas.py",
        "frontend/__init__.py", "frontend/app.py", "frontend/config.py",
        "frontend/components/__init__.py", "frontend/components/sidebar.py",
        "frontend/components/header.py", "frontend/components/cards.py",
        "frontend/views/__init__.py", "frontend/views/dashboard.py",
        "frontend/views/cargar_archivo.py", "frontend/views/ordenar.py",
        "frontend/views/buscar.py", "frontend/views/resultados.py",
        "frontend/views/exportar.py", "frontend/views/comparar.py",
    ]
    for e in esperados:
        if os.path.exists(os.path.join(RAIZ, *e.split("/"))):
            ok(e)
        else:
            error(f"Falta {e}")
    for d in ["datos", "resultados", "Ordenamiento", "ordenamientos1_anaya",
              "ADA3 - MetOrdenaExt", "ADA4_Busqueda"]:
        if os.path.isdir(os.path.join(RAIZ, d)):
            ok(f"carpeta {d}/")
        else:
            aviso(f"No existe la carpeta {d}/")
    for d in ["README.md", "requirements.txt"]:
        if not os.path.exists(os.path.join(RAIZ, d)):
            aviso(f"Falta {d}")


# ------------------------------------------------------------------ 2
def backend():
    titulo("2. FIRMAS REALES DE LA CLASE Sesion")
    try:
        mod = importlib.import_module("backend")
    except Exception as e:
        error(f"No se pudo importar backend.py: {type(e).__name__}: {e}")
        return None
    clase = getattr(mod, "Sesion", None)
    if clase is None:
        error("backend.py no define la clase Sesion")
        return None
    miembros = set()
    for nombre, obj in inspect.getmembers(clase):
        if nombre.startswith("_") and nombre != "__init__":
            continue
        miembros.add(nombre)
        if inspect.isfunction(obj):
            print(f"  método     {nombre}{inspect.signature(obj)}")
        elif isinstance(obj, property):
            print(f"  propiedad  {nombre}")
    try:
        inst = clase()
        ok("Sesion() se instancia sin argumentos")
        for p in ["cargado", "ordenado", "total", "nombre_archivo"]:
            try:
                print(f"    estado inicial {p} = {getattr(inst, p)!r}")
            except Exception as e:
                aviso(f"Propiedad {p} falla en estado inicial: {e}")
    except TypeError as e:
        error(f"Sesion() requiere argumentos: {e}")
    except Exception as e:
        error(f"Sesion() falló: {type(e).__name__}: {e}")
    for esperado in ["cargar", "ordenar", "buscar", "primeros", "ultimos", "exportar", "comparar"]:
        if esperado not in miembros:
            error(f"Sesion no tiene el método {esperado}")
    return miembros


# ------------------------------------------------------------------ 3
def frontend_llamadas(miembros):
    titulo("3. LLAMADAS DEL FRONTEND A Sesion")
    carpeta = os.path.join(RAIZ, "frontend")
    if not os.path.isdir(carpeta):
        error("No existe frontend/")
        return
    instancias = []
    for ruta in archivos_py():
        if not ruta.startswith(carpeta):
            continue
        arbol = parsear(ruta)
        if arbol is None:
            continue
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call):
                f = nodo.func
                nombre = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if nombre == "Sesion":
                    instancias.append(f"{rel(ruta)}:{nodo.lineno}")
            if isinstance(nodo, ast.Attribute) and miembros is not None:
                v = nodo.value
                es_sesion = (isinstance(v, ast.Name) and v.id.lower() in {"sesion", "session"}) or \
                            (isinstance(v, ast.Attribute) and v.attr.lower() in {"sesion", "session"})
                if es_sesion and nodo.attr not in miembros:
                    error(f"{rel(ruta)}:{nodo.lineno} usa sesion.{nodo.attr}, que NO existe en Sesion")
    if len(instancias) == 1:
        ok(f"Una sola instancia de Sesion creada en {instancias[0]}")
    elif not instancias:
        aviso("El frontend no crea ninguna instancia de Sesion")
    else:
        error("Hay varias instancias de Sesion (las vistas no compartirían estado): " + ", ".join(instancias))


# ------------------------------------------------------------------ 4
def resolver_import(ruta, nodo):
    """Devuelve texto de error si el import no resuelve, None si está bien."""
    if isinstance(nodo, ast.Import):
        for a in nodo.names:
            if importlib.util.find_spec(a.name.split(".")[0]) is None:
                return f"import {a.name} (módulo no instalado/encontrado)"
        return None
    if nodo.level > 0:
        base = os.path.dirname(ruta)
        for _ in range(nodo.level - 1):
            base = os.path.dirname(base)
        partes = (nodo.module or "").split(".") if nodo.module else []
        destino = os.path.join(base, *partes)
        if not (os.path.isdir(destino) or os.path.isfile(destino + ".py")):
            return f"from {'.' * nodo.level}{nodo.module or ''} (no existe {rel(destino)})"
        return None
    raiz = (nodo.module or "").split(".")[0]
    if importlib.util.find_spec(raiz) is None:
        return f"from {nodo.module} (módulo no encontrado)"
    return None


def imports():
    titulo("4. IMPORTACIONES")
    malos = 0
    for ruta in archivos_py():
        arbol = parsear(ruta)
        if arbol is None:
            continue
        for nodo in ast.walk(arbol):
            if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                try:
                    r = resolver_import(ruta, nodo)
                except (ImportError, ValueError):
                    r = None
                if r:
                    malos += 1
                    error(f"{rel(ruta)}:{nodo.lineno} -> {r}")
    if not malos:
        ok("Todas las importaciones resuelven")


# ------------------------------------------------------------------ 5
def prohibidos():
    titulo("5. USO DE sort()/sorted() Y LIBRERÍAS PROHIBIDAS (todo el proyecto)")
    hallados = 0
    for ruta in archivos_py():
        arbol = parsear(ruta)
        if arbol is None:
            continue
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call):
                f = nodo.func
                if isinstance(f, ast.Name) and f.id in PROHIBIDOS_NOMBRE:
                    hallados += 1
                    error(f"{rel(ruta)}:{nodo.lineno} usa {f.id}()")
                elif isinstance(f, ast.Attribute) and f.attr in PROHIBIDOS_ATTR:
                    hallados += 1
                    error(f"{rel(ruta)}:{nodo.lineno} usa .{f.attr}()")
            if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                nombres = [a.name for a in nodo.names] if isinstance(nodo, ast.Import) else [nodo.module or ""]
                for n in nombres:
                    if n.split(".")[0] in PROHIBIDOS_MODULO:
                        hallados += 1
                        aviso(f"{rel(ruta)}:{nodo.lineno} importa {n} (revisar si está permitido)")
    if not hallados:
        ok("No se detectó sort()/sorted() ni librerías dudosas")


# ------------------------------------------------------------------ 6
def reutilizacion():
    titulo("6. ¿EL BACKEND USA REALMENTE LAS LIBRERÍAS ORIGINALES?")
    carpetas = ["Ordenamiento", "ordenamientos1_anaya", "ADA3 - MetOrdenaExt", "ADA4_Busqueda"]
    modulos_backend = ["backend", "archivos", "busquedas", "ordenamientos_internos",
                       "ordenamientos_externos", "main"]
    for m in modulos_backend:
        ruta = os.path.join(RAIZ, m + ".py")
        if not os.path.exists(ruta):
            continue
        arbol = parsear(ruta)
        if arbol is None:
            continue
        usa = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom) and nodo.module:
                usa.add(nodo.module)
            elif isinstance(nodo, ast.Import):
                usa.update(a.name for a in nodo.names)
        print(f"  {m}.py importa: {sorted_texto(usa)}")
        with open(ruta, "r", encoding="utf-8") as fh:
            texto = fh.read()
        for c in carpetas:
            if c in texto:
                ok(f"{m}.py hace referencia a '{c}'")
    aviso("Revisar manualmente: si ningún módulo del backend menciona las carpetas originales, "
          "los algoritmos están reimplementados y no reutilizados")


def sorted_texto(conjunto):
    # Sin usar sorted(): inserción simple, para no violar la regla del examen en el propio script
    lista = list(conjunto)
    for i in range(1, len(lista)):
        x, j = lista[i], i - 1
        while j >= 0 and lista[j] > x:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = x
    return ", ".join(lista) if lista else "(nada)"


# ------------------------------------------------------------------ 7
def arranque():
    titulo("7. IMPORT DE frontend.app Y pruebas.py")
    cmd = [sys.executable, "-c",
           "import frontend.app as a; print('import OK;', [n for n in dir(a) if not n.startswith('_')][:12])"]
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        ok(r.stdout.strip())
    else:
        error("frontend.app no se puede importar:\n" + r.stderr.strip()[-1500:])
    ruta = os.path.join(RAIZ, "pruebas.py")
    if os.path.exists(ruta):
        try:
            r = subprocess.run([sys.executable, "pruebas.py"], cwd=RAIZ,
                               capture_output=True, text=True, timeout=180)
            print("  --- salida de pruebas.py (últimas líneas) ---")
            print("\n".join(("  " + l) for l in (r.stdout + r.stderr).strip().splitlines()[-25:]))
            if r.returncode != 0:
                error(f"pruebas.py terminó con código {r.returncode}")
            else:
                ok("pruebas.py terminó sin errores")
        except subprocess.TimeoutExpired:
            aviso("pruebas.py tardó más de 180 s")


def main():
    print("AUDITORÍA DATAFLOW  |  Python " + sys.version.split()[0] + "  |  " + RAIZ)
    estructura()
    miembros = backend()
    frontend_llamadas(miembros)
    imports()
    prohibidos()
    reutilizacion()
    arranque()
    titulo("RESUMEN")
    print(f"  Hallazgos: {len(problemas)}")


if __name__ == "__main__":
    main()
