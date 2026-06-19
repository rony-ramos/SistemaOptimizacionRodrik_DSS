import os
import glob

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
