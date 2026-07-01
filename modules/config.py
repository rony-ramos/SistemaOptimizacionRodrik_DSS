import os
import glob

# Configuración de Negocio
def get_presupuesto_limite(model_path):
    """Extrae dinámicamente el presupuesto límite definido en el archivo LINGO."""
    if not model_path or not os.path.exists(model_path):
        return 1200000.00
    try:
        import re
        with open(model_path, "r", encoding="latin-1") as f:
            content = f.read()
        # Buscar la definición de la variable PRESUPUESTO (ej. PRESUPUESTO = 1200000;)
        match = re.search(r'PRESUPUESTO\s*=\s*(\d+(\.\d+)?)', content, re.IGNORECASE)
        if match:
            return float(match.group(1))
    except Exception as e:
        print(f"Error al extraer presupuesto de LINGO: {e}")
    return 1200000.00


# Configuración SQL Server
SERVER_SQL = r"DESKTOP-KDQUSML\SQLEXPRESS"
DB_NAME = "RODRIK_TRANSPORT_OPTIMIZATION"
CONN_STR = f'DRIVER={{SQL Server}};SERVER={SERVER_SQL};DATABASE={DB_NAME};Trusted_Connection=yes;'

def get_lingo_executable():
    """Busca dinámicamente el ejecutable de LINGO priorizando RunLingo.exe para mejor rendimiento."""
    rutas_comunes = [
        r"C:\LINGO64_22", r"C:\LINGO64_21", r"C:\LINGO64_20", 
        r"C:\LINGO64_19", r"C:\LINGO64_18", r"C:\LINGO"
    ]
    for ruta in rutas_comunes:
        runlingo = os.path.join(ruta, "RunLingo.exe")
        if os.path.exists(runlingo):
            return runlingo
        # Fallback a la GUI si no existe RunLingo
        guis = glob.glob(os.path.join(ruta, "Lingo64_*.exe"))
        if guis:
            return guis[0]
    return ""

def get_modelo_path():
    """Busca el archivo del modelo LINGO de forma resiliente en el directorio actual y el padre."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_dir = os.path.abspath(".")
    
    parent_dir = os.path.dirname(base_dir) # IOP2
    grandparent_dir = os.path.dirname(parent_dir)
    
    for search_dir in [parent_dir, grandparent_dir]:
        for ext in ["*.lng"]:
            archivos = glob.glob(os.path.join(search_dir, ext))
            for f in archivos:
                if "LINGO" in os.path.basename(f).upper():
                    return f
    return ""

LINGO_EXE_PATH = get_lingo_executable()
MODELO_PATH = get_modelo_path()
PRESUPUESTO_LIMITE = get_presupuesto_limite(MODELO_PATH)
