import pyodbc
import pandas as pd
from .config import CONN_STR

def test_connection():
    """Prueba la conexión a la base de datos."""
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RESULTADOS_OPTIMIZACION")
        conn.close()
        return True, "✅ Conexión a BD exitosa"
    except Exception as e:
        return False, f"❌ Error conectando a BD: {e}"

def fetch_oferta():
    """Obtiene la oferta de la base de datos."""
    conn = pyodbc.connect(CONN_STR)
    query_o = """
              SELECT o.nombre_origen, p.nombre_producto, per.semana_num, ofr.cantidad_tn
              FROM OFERTA ofr
                       JOIN ORIGEN o ON ofr.id_origen = o.id_origen
                       JOIN PRODUCTO p ON ofr.id_producto = p.id_producto
                       JOIN PERIODO per ON ofr.id_periodo = per.id_periodo
              ORDER BY o.nombre_origen, p.nombre_producto, per.semana_num
              """
    df_o = pd.read_sql(query_o, conn)
    conn.close()
    return df_o

def fetch_demanda():
    """Obtiene la demanda de la base de datos."""
    conn = pyodbc.connect(CONN_STR)
    query_d = """
              SELECT d.nombre_destino, p.nombre_producto, per.semana_num, dem.cantidad_tn
              FROM DEMANDA dem
                       JOIN DESTINO d ON dem.id_destino = d.id_destino
                       JOIN PRODUCTO p ON dem.id_producto = p.id_producto
                       JOIN PERIODO per ON dem.id_periodo = per.id_periodo
              ORDER BY d.nombre_destino, p.nombre_producto, per.semana_num
              """
    df_d = pd.read_sql(query_d, conn)
    conn.close()
    return df_d

def check_compatibilidad(conn_externa=None):
    """Verifica la restricción de compatibilidad entre camiones y productos."""
    conn_check = conn_externa if conn_externa else pyodbc.connect(CONN_STR)
    query_compatibilidad = """
        SELECT 
            c.tipo_camion,
            p.nombre_producto,
            SUM(r.num_viajes) AS total_viajes
        FROM RESULTADOS_OPTIMIZACION r
        JOIN CAMION c ON r.tipo_camion = UPPER(REPLACE(c.tipo_camion, ' ', '_'))
        JOIN PRODUCTO p ON r.nombre_producto = UPPER(REPLACE(p.nombre_producto, ' ', '_'))
        LEFT JOIN VALIDA_CAMION_PRODUCTO v
            ON c.id_camion = v.id_camion
        AND p.id_producto = v.id_producto
        AND v.estado = 1
        WHERE r.num_viajes > 0
        AND v.id_valida IS NULL
        GROUP BY c.tipo_camion, p.nombre_producto
    """
    df_compatibilidad = pd.read_sql(query_compatibilidad, conn_check)
    if not conn_externa:
        conn_check.close()
    return df_compatibilidad

def check_disponibilidad(conn_externa=None):
    """Verifica la disponibilidad de viajes por camión y periodo."""
    conn_check = conn_externa if conn_externa else pyodbc.connect(CONN_STR)
    query_disponibilidad = """
        SELECT 
            c.tipo_camion,
            pe.nombre_periodo,
            SUM(r.num_viajes) AS viajes_asignados,
            dc.cantidad_viajes AS viajes_disponibles
        FROM RESULTADOS_OPTIMIZACION r
        JOIN CAMION c ON r.tipo_camion = UPPER(REPLACE(c.tipo_camion, ' ', '_'))
        JOIN PERIODO pe ON r.semana = UPPER(REPLACE(pe.nombre_periodo, ' ', '_'))
        JOIN DISPONIBILIDAD_CAMION dc
            ON c.id_camion = dc.id_camion
        AND pe.id_periodo = dc.id_periodo
        WHERE r.num_viajes > 0
        GROUP BY 
            c.tipo_camion,
            pe.nombre_periodo,
            dc.cantidad_viajes
        HAVING SUM(r.num_viajes) > dc.cantidad_viajes
    """
    df_disponibilidad = pd.read_sql(query_disponibilidad, conn_check)
    if not conn_externa:
        conn_check.close()
    return df_disponibilidad

def fetch_resultados_optimizacion(conn):
    """Obtiene los resultados principales de optimización."""
    query_res = """
                SELECT r.nombre_origen,
                       r.nombre_destino,
                       r.tipo_camion,
                       r.nombre_producto,
                       r.semana,
                       r.num_viajes,
                       c.capacidad_efectiva,
                       c.costo_fijo,
                       co.costo_base
                FROM RESULTADOS_OPTIMIZACION r
                         LEFT JOIN CAMION c ON r.tipo_camion = UPPER(REPLACE(c.tipo_camion, ' ', '_'))
                         LEFT JOIN (SELECT o.nombre_origen, d.nombre_destino, p.nombre_producto, co.costo_base
                                    FROM COSTO co
                                             JOIN ORIGEN o ON co.id_origen = o.id_origen
                                             JOIN DESTINO d ON co.id_destino = d.id_destino
                                             JOIN PRODUCTO p ON co.id_producto = p.id_producto) co
                                   ON r.nombre_origen = UPPER(REPLACE(co.nombre_origen, ' ', '_')) AND
                                      r.nombre_destino = UPPER(REPLACE(co.nombre_destino, ' ', '_')) AND
                                      r.nombre_producto = UPPER(REPLACE(co.nombre_producto, ' ', '_'))
                WHERE r.num_viajes > 0.001
                """
    return pd.read_sql(query_res, conn)

def fetch_faltantes(conn):
    """Obtiene la cantidad total de faltantes."""
    query_falta = "SELECT SUM(cantidad_falta) AS Total_Falta_TN FROM RESULTADOS_FALTA"
    return pd.read_sql(query_falta, conn)

def fetch_demanda_total(conn):
    """Obtiene la demanda total en toneladas."""
    query_demanda = "SELECT SUM(cantidad_tn) as total FROM DEMANDA"
    return pd.read_sql(query_demanda, conn)

def fetch_camiones():
    """Obtiene los camiones disponibles."""
    conn = pyodbc.connect(CONN_STR)
    query = "SELECT tipo_camion, capacidad_efectiva, especializacion, costo_fijo FROM CAMION WHERE estado=1 ORDER BY id_camion"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_matriz_compatibilidad():
    """Obtiene la matriz de compatibilidad camión-producto."""
    conn = pyodbc.connect(CONN_STR)
    query = """
        SELECT c.tipo_camion, p.nombre_producto, v.es_valido 
        FROM VW_MATRIZ_COMPATIBILIDAD v
        JOIN CAMION c ON v.id_camion = c.id_camion
        JOIN PRODUCTO p ON v.id_producto = p.id_producto
        ORDER BY c.id_camion, p.id_producto
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_disponibilidad_camiones():
    """Obtiene la disponibilidad de viajes por camión y periodo."""
    conn = pyodbc.connect(CONN_STR)
    query = """
        SELECT c.tipo_camion, pe.nombre_periodo, d.cantidad_viajes
        FROM DISPONIBILIDAD_CAMION d
        JOIN CAMION c ON d.id_camion = c.id_camion
        JOIN PERIODO pe ON d.id_periodo = pe.id_periodo
        WHERE d.estado=1
        ORDER BY c.id_camion, pe.id_periodo
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_tarifario():
    """Obtiene el tarifario de costo base."""
    conn = pyodbc.connect(CONN_STR)
    query = """
        SELECT o.nombre_origen, d.nombre_destino, p.nombre_producto, c.costo_base
        FROM COSTO c
        JOIN ORIGEN o ON c.id_origen = o.id_origen
        JOIN DESTINO d ON c.id_destino = d.id_destino
        JOIN PRODUCTO p ON c.id_producto = p.id_producto
        ORDER BY o.id_origen, d.id_destino, p.id_producto
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_faltantes_detalle(conn):
    """Obtiene el detalle de faltantes por destino, producto y semana."""
    query = "SELECT nombre_destino, nombre_producto, semana, cantidad_falta FROM RESULTADOS_FALTA WHERE cantidad_falta > 0.001"
    return pd.read_sql(query, conn)
