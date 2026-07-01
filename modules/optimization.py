import subprocess
import os
import time

def run_lingo_model(lingo_path, model_path):
    """Ejecuta el modelo LINGO usando subprocess y un script .ltf temporal."""
    if not lingo_path or not os.path.exists(lingo_path): 
        raise FileNotFoundError("❌ No se encontró automáticamente el ejecutable de LINGO en las rutas habituales (C:\\LINGO64_...).")
    if not model_path or not os.path.exists(model_path): 
        raise FileNotFoundError("❌ No se encontró el modelo de LINGO (.lng o .lg4) en la carpeta del script ni en la carpeta superior.")

    script_abs = os.path.abspath("run_cmd.ltf")
    modelo_nombre = os.path.basename(model_path)
    # with open(script_abs, "w") as f:
    #     f.write("SET ECHOIN 1\n")
    #     f.write("SET TERSEO 0\n")
    #     f.write(f'TAKE {modelo_nombre}\n')
    #     f.write("GO\n")
    #     f.write("QUIT\n")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    t_inicio_lingo = time.time()
    # Limpiar tablas de resultados antes de ejecutar
    try:
        import pyodbc
        from .config import CONN_STR
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        # Truncar y prellenar tablas para que LINGO actualice en lugar de intentar insertar
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
        conn.close()

        proceso = subprocess.run(
            [lingo_path, script_abs], 
            capture_output=True, 
            text=True, 
            timeout=300, 
            startupinfo=startupinfo,
            cwd=os.path.dirname(model_path)
        )
    except Exception as e:
        print(f"Error truncando tablas: {e}")
    # finally:
    #     if os.path.exists(script_abs): 
    #         os.remove(script_abs)

    t_fin_lingo = time.time()
    return proceso, t_fin_lingo - t_inicio_lingo


def calculate_metrics(df_res, df_falta, demanda_total_df):
    """Calcula el costo operativo real y el costo total de la función objetivo."""
    MULTA_COEFICIENTE = 300  # Valor de diagnóstico

    # 1. CÁLCULO DE COSTOS OPERACIONALES
    df_res['volumen_tn'] = df_res['num_viajes'] * df_res['capacidad_efectiva']
    df_res['Y_flag'] = (df_res['num_viajes'] > 0).astype(int)
    df_res['costo_fijo_total'] = df_res['costo_fijo'] * df_res['Y_flag']
    df_res['costo_variable'] = df_res['costo_base'] * df_res['volumen_tn']
    df_res['costo_total_operativo'] = df_res['costo_variable'] + df_res['costo_fijo_total']

    # 2. CÁLCULO DE COSTO DE PENALIDAD Y AGREGACIÓN FINAL
    costo_penalidad_falta = 0.0
    if not df_falta.empty and df_falta.iloc[0, 0] is not None:
        toneladas_faltantes = df_falta.iloc[0, 0]
        costo_penalidad_falta = toneladas_faltantes * MULTA_COEFICIENTE

    total_costo_operativo_real = df_res['costo_total_operativo'].sum()

    total_viajes = df_res['num_viajes'].sum()
    total_volumen = df_res['volumen_tn'].sum()

    demanda_total = demanda_total_df.iloc[0, 0] if not demanda_total_df.empty else 0

    return df_res, total_costo_operativo_real, costo_penalidad_falta, total_viajes, total_volumen, demanda_total
