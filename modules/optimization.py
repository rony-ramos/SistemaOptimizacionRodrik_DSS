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
    modelo_abs = os.path.abspath(model_path)
    with open(script_abs, "w") as f:
        f.write("SET ECHOIN 1\n")
        f.write("SET TERSEO 0\n")
        f.write(f'TAKE "{modelo_abs}"\n')
        f.write("GO\n")
        f.write("QUIT\n")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    t_inicio_lingo = time.time()
    try:
        proceso = subprocess.run(
            [lingo_path, script_abs], capture_output=True, text=True, timeout=300, startupinfo=startupinfo
        )
    finally:
        if os.path.exists(script_abs): 
            os.remove(script_abs)

    t_fin_lingo = time.time()
    return proceso, t_fin_lingo - t_inicio_lingo


def calculate_metrics(df_res, df_falta, demanda_total_df):
    """Calcula el costo operativo real y el costo total de la función objetivo."""
    MULTA_COEFICIENTE = 10000  # Valor de diagnóstico

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
    total_costo_final_fo = total_costo_operativo_real + costo_penalidad_falta

    total_viajes = df_res['num_viajes'].sum()
    total_volumen = df_res['volumen_tn'].sum()

    demanda_total = demanda_total_df.iloc[0, 0] if not demanda_total_df.empty else 0

    return df_res, total_costo_final_fo, total_viajes, total_volumen, demanda_total
