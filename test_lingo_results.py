import pyodbc
import pandas as pd
import subprocess
import os
import time
from modules.config import CONN_STR, LINGO_EXE_PATH, MODELO_PATH

def run_tests():
    try:
        print(f"Usando LINGO en: {LINGO_EXE_PATH}")
        print(f"Usando Modelo en: {MODELO_PATH}")
        
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        print("\nConectado a la BD.")
        
        # 1. Truncar y prellenar
        print("Truncando y prellenando tablas...")
        cursor.execute("TRUNCATE TABLE RESULTADOS_OPTIMIZACION")
        cursor.execute("TRUNCATE TABLE RESULTADOS_X")
        cursor.execute("TRUNCATE TABLE RESULTADOS_FALTA")
        
        cursor.execute("""
            INSERT INTO RESULTADOS_FALTA (nombre_destino, nombre_producto, semana, cantidad_falta)
            SELECT d.nombre_destino, p.nombre_producto, pe.nombre_periodo, 0.0
            FROM DESTINO d CROSS JOIN PRODUCTO p CROSS JOIN PERIODO pe
            ORDER BY d.id_destino, p.id_producto, pe.id_periodo;
        """)
        
        cursor.execute("""
            INSERT INTO RESULTADOS_OPTIMIZACION (nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, num_viajes)
            SELECT o.nombre_origen, d.nombre_destino, c.tipo_camion, p.nombre_producto, pe.nombre_periodo, 0.0
            FROM ORIGEN o CROSS JOIN DESTINO d CROSS JOIN CAMION c CROSS JOIN PRODUCTO p CROSS JOIN PERIODO pe
            ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;
        """)
        
        cursor.execute("""
            INSERT INTO RESULTADOS_X (nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, cantidad_tn)
            SELECT o.nombre_origen, d.nombre_destino, c.tipo_camion, p.nombre_producto, pe.nombre_periodo, 0.0
            FROM ORIGEN o CROSS JOIN DESTINO d CROSS JOIN CAMION c CROSS JOIN PRODUCTO p CROSS JOIN PERIODO pe
            ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;
        """)
        conn.commit()
        print("Tablas prellenadas correctamente.")
        
        # 2. Correr LINGO
        print("\nEjecutando LINGO...")
        import ctypes
        from ctypes import wintypes
        def get_short_path_name(long_name):
            _GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
            _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
            _GetShortPathNameW.restype = wintypes.DWORD
            output_buf_size = 0
            while True:
                output_buf = ctypes.create_unicode_buffer(output_buf_size)
                needed = _GetShortPathNameW(long_name, output_buf, output_buf_size)
                if needed == 0: return long_name
                if needed <= output_buf_size: return output_buf.value
                output_buf_size = needed

        script_abs = os.path.abspath("run_cmd.ltf")
        modelo_nombre = os.path.basename(MODELO_PATH)
        with open(script_abs, "w") as f:
            f.write("SET ECHOIN 1\n")
            f.write("SET TERSEO 0\n")
            f.write(f'TAKE {modelo_nombre}\n')
            f.write("GO\n")
            f.write("QUIT\n")

        proceso = subprocess.run(
            [LINGO_EXE_PATH, script_abs], 
            capture_output=True, 
            text=True, 
            timeout=300,
            cwd=os.path.dirname(MODELO_PATH)
        )
        
        print("\n================ SALIDA DE LINGO ================")
        print(proceso.stdout)
        if proceso.stderr:
            print("ERRORES:")
            print(proceso.stderr)
        print("=================================================")
        
        # 3. Ver resultados en DB
        query_viajes = "SELECT SUM(num_viajes) FROM RESULTADOS_OPTIMIZACION"
        total_viajes = pd.read_sql(query_viajes, conn).iloc[0,0]
        print(f"\nSuma total de viajes en BD despues de LINGO: {total_viajes}")

        if total_viajes == 0 or total_viajes is None:
            print("LINGO no guardo ningun viaje en la base de datos (TODO ES CERO). Revisa el log de LINGO arriba.")
        else:
            query_top = "SELECT TOP 5 * FROM RESULTADOS_OPTIMIZACION WHERE num_viajes > 0"
            df_top = pd.read_sql(query_top, conn)
            print("\nPrimeras filas con viajes:")
            print(df_top.to_string())
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run_tests()
