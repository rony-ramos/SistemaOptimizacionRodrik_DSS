import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyodbc
import subprocess
import os
import pandas as pd
from threading import Thread
import warnings
import time

# Ignorar advertencias de compatibilidad de Pandas
warnings.filterwarnings("ignore")

# =============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA (VERIFICAR RUTAS Y SERVIDOR)
# =============================================================================

import glob

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
    
    parent_dir = os.path.dirname(base_dir)
    
    # Buscar en el directorio actual y un nivel más arriba
    for search_dir in [base_dir, parent_dir]:
        # Preferimos la versión en texto (.lng) a la binaria (.lg4)
        for ext in ["*.lng", "*.lg4"]:
            archivos = glob.glob(os.path.join(search_dir, ext))
            for f in archivos:
                if "MODELO" in os.path.basename(f).upper() and "LINGO" in os.path.basename(f).upper():
                    return f
    return ""

LINGO_EXE_PATH = get_lingo_executable()
MODELO_PATH = get_modelo_path()

# Configuración SQL Server
SERVER_SQL = r"DESKTOP-KDQUSML\SQLEXPRESS"
DB_NAME = "ROQUE_TRANSPORT_OPTIMIZATION"
CONN_STR = f'DRIVER={{SQL Server}};SERVER={SERVER_SQL};DATABASE={DB_NAME};Trusted_Connection=yes;'


class RoqueInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Optimización - Roque Transport E.I.R.L.")
        self.root.geometry("1300x850")
        self.root.configure(bg="#e6e6e6")

        # Inicializar atributos
        self.console = None
        self.lbl_costo_val = None
        self.lbl_viajes_val = None
        self.lbl_servicio_val = None
        self.tree = None

        style = ttk.Style();
        style.theme_use('clam')
        style.configure("TFrame", background="#e6e6e6")

        # --- LLAMADA A LA INTERFAZ VISUAL ---
        self.configurar_interfaz_visual(root)

        # Cargar datos iniciales
        self.cargar_datos_inputs()
        self.log("Sistema inicializado y conectado a SQL.")
        self.log(f"Modelo LINGO: {MODELO_PATH}")
        self.verificar_conexion_bd()

        # --- MÉTODOS AUXILIARES Y UI (Mantienen la estructura original) ---

    def configurar_interfaz_visual(self, root):
        """Contiene todo el código de configuración y posicionamiento de widgets."""

        # --- HEADER SUPERIOR ---
        header_frame = tk.Frame(root, bg="#003366", pady=15)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="OPTIMIZACIÓN DE TRANSPORTE Y LOGÍSTICA",
                 font=("Arial", 22, "bold"), bg="#003366", fg="white").pack()
        tk.Label(header_frame, text="Modelo de Programación por Metas (LINGO 20 + SQL Server)",
                 font=("Arial", 10), bg="#003366", fg="#cccccc").pack()

        # --- ÁREA SCROLLABLE ---
        main_canvas = tk.Canvas(root, bg="#e6e6e6")
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- SECCIONES ---
        self.crear_seccion_oferta()
        self.crear_seccion_demanda()

        # 2. Botonera Principal
        btn_frame = tk.Frame(self.scrollable_frame, bg="#e6e6e6", pady=20)
        btn_frame.pack(fill="x", padx=20)

        tk.Button(btn_frame, text="🔄 Recargar Datos SQL", bg="#17a2b8", fg="white", width=20,
                  command=self.cargar_datos_inputs).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔍 Verificar Restricciones", bg="#6c757d", fg="white", width=20,
                  command=self.verificar_restricciones).pack(side="left", padx=5)

        self.btn_optimizar = tk.Button(btn_frame, text="▶ EJECUTAR OPTIMIZACIÓN", bg="#28a745", fg="white",
                                       font=("Arial", 12, "bold"), width=30, height=2,
                                       command=self.iniciar_optimizacion)
        self.btn_optimizar.pack(side="right", padx=20)

        self.lbl_status = tk.Label(btn_frame, text="Estado: Listo", font=("Arial", 11, "italic"), bg="#e6e6e6",
                                   fg="#555")
        self.lbl_status.pack(side="right", padx=10)

        # 3. Resumen Ejecutivo (Tarjetas)
        self.resumen_frame = tk.Frame(self.scrollable_frame, bg="#e6e6e6")
        self.resumen_frame.pack(fill="x", padx=20, pady=10)

        self.card_costo = self.crear_tarjeta(self.resumen_frame, "Costo Total Operativo", "S/ 0.00", "#dc3545")
        self.card_viajes = self.crear_tarjeta(self.resumen_frame, "Total Viajes", "0", "#007bff")
        self.card_servicio = self.crear_tarjeta(self.resumen_frame, "Nivel de Servicio", "0%", "#ffc107")

        self.card_costo.pack(side="left", expand=True, fill="x", padx=5)
        self.card_viajes.pack(side="left", expand=True, fill="x", padx=5)
        self.card_servicio.pack(side="left", expand=True, fill="x", padx=5)

        # 4. Tabla de Detalles (Treeview)
        lbl_det = tk.Label(self.scrollable_frame, text="Detalle de Envíos Programados",
                           font=("Arial", 12, "bold"), bg="#e6e6e6", anchor="w")
        lbl_det.pack(fill="x", padx=20, pady=(20, 5))

        cols = ("Origen", "Destino", "Camión", "Producto", "Semana", "Viajes (N)", "Volumen (TN)", "Costo (S/)")
        self.tree = ttk.Treeview(self.scrollable_frame, columns=cols, show="headings", height=15)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="x", padx=20, pady=5)

        # 5. Consola de Logs
        lbl_log = tk.Label(self.scrollable_frame, text="Log de Ejecución",
                           font=("Arial", 12, "bold"), bg="#e6e6e6", anchor="w")
        lbl_log.pack(fill="x", padx=20, pady=(20, 5))

        self.console = scrolledtext.ScrolledText(self.scrollable_frame, height=8, bg="#1e1e1e", fg="#00ff00",
                                                 font=("Consolas", 9))
        self.console.pack(fill="x", padx=20, pady=5)

    def verificar_conexion_bd(self):
        """Verificar conexión a BD al inicio (aislado de la lógica de optimización)"""
        try:
            conn = pyodbc.connect(CONN_STR)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM RESULTADOS_OPTIMIZACION")
            conn.close()
            self.log("✅ Conexión a BD exitosa")
        except Exception as e:
            self.log(f"❌ Error conectando a BD: {e}");
            messagebox.showerror("Error BD", f"No se pudo conectar a la base de datos:\n{e}")

    def log(self, mensaje):
        """Agregar mensaje a la consola"""
        if hasattr(self, 'console') and self.console:
            timestamp = time.strftime("%H:%M:%S")
            self.console.insert(tk.END, f"[{timestamp}] {mensaje}\n");
            self.console.see(tk.END);
            self.root.update()
        else:
            print(f"LOG: {mensaje}")

    def crear_tarjeta(self, parent, titulo, valor, color):
        f = tk.Frame(parent, bg="white", bd=1, relief="solid")
        tk.Frame(f, bg=color, height=4).pack(fill="x")
        tk.Label(f, text=titulo, bg="white", fg="#666").pack(pady=(10, 0))
        lbl = tk.Label(f, text=valor, bg="white", font=("Arial", 18, "bold"), fg="#333")
        lbl.pack(pady=(5, 15))

        if titulo == "Costo Total Operativo":
            self.lbl_costo_val = lbl
        elif titulo == "Total Viajes":
            self.lbl_viajes_val = lbl
        elif titulo == "Nivel de Servicio":
            self.lbl_servicio_val = lbl
        return f

    def crear_seccion_oferta(self):
        frame = tk.LabelFrame(self.scrollable_frame, text="OFERTA SEMANAL (TN)", font=("Arial", 10, "bold"), bg="white",
                              padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)
        headers = ["Origen", "Producto", "Semana 1", "Semana 2", "Semana 3", "Semana 4"]
        for i, h in enumerate(headers):
            tk.Label(frame, text=h, bg="#eee", font=("Arial", 8, "bold"), width=15).grid(row=0, column=i, sticky="ew",
                                                                                         padx=1)
        self.frame_oferta_grid = frame

    def crear_seccion_demanda(self):
        frame = tk.LabelFrame(self.scrollable_frame, text="DEMANDA SEMANAL (TN)", font=("Arial", 10, "bold"),
                              bg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)
        headers = ["Cliente", "Producto", "Semana 1", "Semana 2", "Semana 3", "Semana 4"]
        for i, h in enumerate(headers):
            tk.Label(frame, text=h, bg="#eee", font=("Arial", 8, "bold"), width=15).grid(row=0, column=i, sticky="ew",
                                                                                         padx=1)
        self.frame_demanda_grid = frame

    # =========================================================================
    # LÓGICA 1: CARGAR INPUTS (LECTURA DIRECTA DE BD)
    # =========================================================================
    def cargar_datos_inputs(self):
        """Carga datos de Oferta y Demanda directamente desde SQL Server."""
        try:
            conn = pyodbc.connect(CONN_STR)
            self.log("Cargando datos de oferta y demanda...")

            # OFERTA
            query_o = """
                      SELECT o.nombre_origen, p.nombre_producto, per.semana_num, ofr.cantidad_tn
                      FROM OFERTA ofr
                               JOIN ORIGEN o ON ofr.id_origen = o.id_origen
                               JOIN PRODUCTO p ON ofr.id_producto = p.id_producto
                               JOIN PERIODO per ON ofr.id_periodo = per.id_periodo
                      ORDER BY o.nombre_origen, p.nombre_producto, per.semana_num \
                      """
            df_o = pd.read_sql(query_o, conn)

            for widget in self.frame_oferta_grid.grid_slaves():
                if int(widget.grid_info()["row"]) > 0: widget.destroy()
            row_idx = 1
            for (org, prod), grupo in df_o.groupby(['nombre_origen', 'nombre_producto']):
                tk.Label(self.frame_oferta_grid, text=org, bg="white").grid(row=row_idx, column=0, sticky="nsew",
                                                                            padx=1)
                tk.Label(self.frame_oferta_grid, text=prod, bg="white").grid(row=row_idx, column=1, sticky="nsew",
                                                                             padx=1)
                for sem in range(1, 5):
                    val = grupo[grupo['semana_num'] == sem]['cantidad_tn'].sum()
                    e = tk.Entry(self.frame_oferta_grid, justify="center", bg="#f9f9f9");
                    e.insert(0, f"{val:.0f}");
                    e.grid(row=row_idx, column=sem + 1, sticky="ew", padx=1)
                row_idx += 1

            # DEMANDA
            query_d = """
                      SELECT d.nombre_destino, p.nombre_producto, per.semana_num, dem.cantidad_tn
                      FROM DEMANDA dem
                               JOIN DESTINO d ON dem.id_destino = d.id_destino
                               JOIN PRODUCTO p ON dem.id_producto = p.id_producto
                               JOIN PERIODO per ON dem.id_periodo = per.id_periodo
                      ORDER BY d.nombre_destino, p.nombre_producto, per.semana_num \
                      """
            df_d = pd.read_sql(query_d, conn)

            for widget in self.frame_demanda_grid.grid_slaves():
                if int(widget.grid_info()["row"]) > 0: widget.destroy()
            row_idx = 1
            for (dest, prod), grupo in df_d.groupby(['nombre_destino', 'nombre_producto']):
                tk.Label(self.frame_demanda_grid, text=dest, bg="white").grid(row=row_idx, column=0, sticky="nsew",
                                                                              padx=1)
                tk.Label(self.frame_demanda_grid, text=prod, bg="white").grid(row=row_idx, column=1, sticky="nsew",
                                                                              padx=1)
                for sem in range(1, 5):
                    val = grupo[grupo['semana_num'] == sem]['cantidad_tn'].sum()
                    e = tk.Entry(self.frame_demanda_grid, justify="center", bg="#f9f9f9");
                    e.insert(0, f"{val:.0f}");
                    e.grid(row=row_idx, column=sem + 1, sticky="ew", padx=1)
                row_idx += 1

            conn.close()
            self.log("✅ Datos cargados correctamente")

        except Exception as e:
            self.log(f"❌ Error cargando inputs: {e}");
            messagebox.showerror("Error", f"Error cargando datos:\n{e}")

    # =========================================================================
    # VERIFICAR RESTRICCIONES (USA CONEXIÓN INTERNA AISLADA)
    # =========================================================================
    def verificar_restricciones(self, conn_externa=None):
        """
        [BOTÓN]: Inicia la verificación de exclusividad. Usa conn_externa si se provee.
        """
        try:
            self.log("Verificando violaciones de exclusividad...");
            
            t0 = time.time()
            conn_check = conn_externa if conn_externa else pyodbc.connect(CONN_STR)

            query = """
                    SELECT r.tipo_camion, r.nombre_producto, SUM(r.num_viajes) as total_viajes
                    FROM RESULTADOS_OPTIMIZACION r
                    WHERE r.num_viajes > 0
                      AND (
                        (r.nombre_producto LIKE '%HELADOS%' AND r.tipo_camion NOT LIKE '%THERMO%')
                            OR
                        (r.nombre_producto NOT LIKE '%HELADOS%' AND r.tipo_camion LIKE '%THERMO%')
                        )
                    GROUP BY r.tipo_camion, r.nombre_producto \
                    """

            df_violaciones = pd.read_sql(query, conn_check)

            if not df_violaciones.empty:
                self.log("❌ VIOLACIONES DE EXCLUSIVIDAD ENCONTRADAS:")
                for _, row in df_violaciones.iterrows():
                    self.log(
                        f"   - {row['tipo_camion']} transportando {row['nombre_producto']}: {row['total_viajes']:.2f} viajes")
                messagebox.showwarning("Restricciones Violadas",
                                       "Se encontraron violaciones de exclusividad. Revisa el modelo LINGO.")
            else:
                self.log("✅ No se encontraron violaciones de exclusividad en los resultados.")

            if not conn_externa:
                conn_check.close()
                
            t1 = time.time()
            self.log(f"[DEBUG] verificar_restricciones tomó {t1-t0:.2f}s")

        except Exception as e:
            self.log(f"❌ Error verificando restricciones: {e}")

    # =========================================================================
    # LÓGICA 2: EJECUTAR OPTIMIZACIÓN (LINGO)
    # =========================================================================
    def iniciar_optimizacion(self):
        if hasattr(self, 'tree') and self.tree:
            for i in self.tree.get_children(): self.tree.delete(i)

        self.btn_optimizar.config(state="disabled", text="PROCESANDO...")
        self.lbl_status.config(text="⏳ Ejecutando Motor LINGO...", fg="#e67e22")
        self.log("Iniciando optimización con LINGO.")

        Thread(target=self.correr_lingo_thread, daemon=True).start()

    def correr_lingo_thread(self):
        try:
            self.log("Verificando archivos y rutas de LINGO...");
            if not LINGO_EXE_PATH or not os.path.exists(LINGO_EXE_PATH): 
                raise FileNotFoundError("❌ No se encontró automáticamente el ejecutable de LINGO en las rutas habituales (C:\\LINGO64_...).")
            if not MODELO_PATH or not os.path.exists(MODELO_PATH): 
                raise FileNotFoundError("❌ No se encontró el modelo de LINGO (.lng o .lg4) en la carpeta del script ni en la carpeta superior.")

            script_abs = os.path.abspath("run_cmd.ltf")
            modelo_abs = os.path.abspath(MODELO_PATH)
            with open(script_abs, "w") as f:
                f.write("SET ECHOIN 1\n");
                f.write("SET TERSEO 0\n");
                f.write(f'TAKE "{modelo_abs}"\n');
                f.write("GO\n");
                f.write("QUIT\n")

            self.log(f"Ejecutando: {LINGO_EXE_PATH}")
            startupinfo = subprocess.STARTUPINFO();
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            t_inicio_lingo = time.time()
            proceso = subprocess.run(
                [LINGO_EXE_PATH, script_abs], capture_output=True, text=True, timeout=300, startupinfo=startupinfo
            )
            t_fin_lingo = time.time()
            self.log(f"[DEBUG] ⏳ Tiempo de ejecución LINGO (subprocess): {t_fin_lingo - t_inicio_lingo:.2f}s")

            if proceso.returncode == 0:
                self.log("✅ LINGO ejecutado exitosamente")
                self.root.after(0, self.leer_resultados_sql)
            else:
                self.log(f"❌ LINGO terminó con errores (Código: {proceso.returncode})");
                self.log(f"Error detallado: {proceso.stderr[:500]}...")
                self.root.after(0, lambda: messagebox.showerror("Error LINGO", proceso.stderr));
                self.root.after(0, self.reactivar_boton)

        except subprocess.TimeoutExpired:
            self.log("❌ LINGO excedió el tiempo límite (5 minutos)");
            self.root.after(0, lambda: messagebox.showerror("Timeout", "LINGO excedió el tiempo límite"));
            self.root.after(0, self.reactivar_boton)
        except Exception as e:
            self.log(f"❌ Error ejecutando LINGO: {e}");
            self.root.after(0, lambda: messagebox.showerror("Error LINGO", str(e)));
            self.root.after(0, self.reactivar_boton)
        finally:
            if os.path.exists("run_cmd.ltf"): os.remove("run_cmd.ltf")

    def reactivar_boton(self):
        """Reactivar botón después de error o fallo"""
        self.btn_optimizar.config(state="normal", text="▶ EJECUTAR OPTIMIZACIÓN")
        self.lbl_status.config(text="❌ Error en ejecución", fg="red")

    # --- MÉTODO PARA EL CÁLCULO DE MÉTRICAS (USADO POR leer_resultados_sql) ---
    def calcular_metricas_y_costo(self, df_res, conn):
        """
        Calcula el costo operativo real y el costo total de la función objetivo.
        """
        MULTA_COEFICIENTE = 10000  # Valor de diagnóstico

        # 1. CÁLCULO DE COSTOS OPERACIONALES
        df_res['volumen_tn'] = df_res['num_viajes'] * df_res['capacidad_efectiva']
        df_res['Y_flag'] = (df_res['num_viajes'] > 0).astype(int)
        df_res['costo_fijo_total'] = df_res['costo_fijo'] * df_res['Y_flag']
        df_res['costo_variable'] = df_res['costo_base'] * df_res['volumen_tn']
        df_res['costo_total_operativo'] = df_res['costo_variable'] + df_res['costo_fijo_total']

        # 2. CÁLCULO DE COSTO DE PENALIDAD Y AGREGACIÓN FINAL
        query_falta = "SELECT SUM(cantidad_falta) AS Total_Falta_TN FROM RESULTADOS_FALTA"
        df_falta = pd.read_sql(query_falta, conn)

        costo_penalidad_falta = 0.0
        if not df_falta.empty and df_falta.iloc[0, 0] is not None:
            toneladas_faltantes = df_falta.iloc[0, 0]
            costo_penalidad_falta = toneladas_faltantes * MULTA_COEFICIENTE

        total_costo_operativo_real = df_res['costo_total_operativo'].sum()
        total_costo_final_fo = total_costo_operativo_real + costo_penalidad_falta

        total_viajes = df_res['num_viajes'].sum()
        total_volumen = df_res['volumen_tn'].sum()

        query_demanda = "SELECT SUM(cantidad_tn) as total FROM DEMANDA"
        demanda_total_df = pd.read_sql(query_demanda, conn)
        demanda_total = demanda_total_df.iloc[0, 0] if not demanda_total_df.empty else 0

        return df_res, total_costo_final_fo, total_viajes, total_volumen, demanda_total

    # --- FUNCIÓN DE LECTURA DE RESULTADOS ---
    def leer_resultados_sql(self):
        self.lbl_status.config(text="📥 Procesando resultados...", fg="blue")
        self.log("Leyendo resultados de la base de datos...")
        t_inicio_sql = time.time()

        try:
            conn = pyodbc.connect(CONN_STR)
            t_conn = time.time()
            self.log(f"[DEBUG] Conexión SQL tomó {t_conn - t_inicio_sql:.2f}s")

            query_res = """
                        SELECT r.nombre_origen, \
                               r.nombre_destino, \
                               r.tipo_camion, \
                               r.nombre_producto,
                               r.semana, \
                               r.num_viajes, \
                               c.capacidad_efectiva, \
                               c.costo_fijo, \
                               co.costo_base
                        FROM RESULTADOS_OPTIMIZACION r \
                                 LEFT JOIN CAMION c ON r.tipo_camion = c.tipo_camion \
                                 LEFT JOIN (SELECT o.nombre_origen, d.nombre_destino, p.nombre_producto, co.costo_base \
                                            FROM COSTO co \
                                                     JOIN ORIGEN o ON co.id_origen = o.id_origen \
                                                     JOIN DESTINO d ON co.id_destino = d.id_destino \
                                                     JOIN PRODUCTO p ON co.id_producto = p.id_producto) co \
                                           ON r.nombre_origen = co.nombre_origen AND \
                                              r.nombre_destino = co.nombre_destino AND \
                                              r.nombre_producto = co.nombre_producto
                        WHERE r.num_viajes > 0.001 \
                        """
            df_res = pd.read_sql(query_res, conn)
            t_query1 = time.time()
            self.log(f"[DEBUG] Lectura df_res tomó {t_query1 - t_conn:.2f}s")

            if df_res.empty:
                self.log("⚠️ No se encontraron envíos programados");
                self.lbl_status.config(text="⚠️ Sin envíos.", fg="orange")
                self.reactivar_boton();
                conn.close();
                return

            self.log(f"📊 Encontrados {len(df_res)} registros de envíos")

            # LLAMADA A CÁLCULO
            df_res, total_costo, total_viajes, total_volumen, demanda_total = self.calcular_metricas_y_costo(df_res,
                                                                                                             conn)
            t_calc = time.time()
            self.log(f"[DEBUG] calcular_metricas_y_costo tomó {t_calc - t_query1:.2f}s")

            # LLAMADA A VERIFICACIÓN
            self.verificar_restricciones(conn)

            # --- ACTUALIZACIÓN DE INTERFAZ ---
            if demanda_total > 0:
                servicio = (total_volumen / demanda_total) * 100
                servicio_text = f"{servicio:.2f}%"

                if servicio < 95.0 or servicio > 105.0:
                    self.lbl_servicio_val.config(text=servicio_text, fg="red"); self.log(
                        f"⚠️ Nivel de servicio: {servicio:.2f}% (Fuera de rango)")
                else:
                    self.lbl_servicio_val.config(text=servicio_text, fg="green"); self.log(
                        f"✅ Nivel de servicio óptimo: {servicio:.2f}%")

            self.lbl_costo_val.config(text=f"S/ {total_costo:,.2f}");
            self.lbl_viajes_val.config(text=f"{int(total_viajes)}")

            self.tree.delete(*self.tree.get_children())
            for _, row in df_res.iterrows():
                costo_detalle = row['costo_total_operativo']
                self.tree.insert("", "end", values=(
                    row['nombre_origen'], row['nombre_destino'], row['tipo_camion'], row['nombre_producto'],
                    row['semana'], f"{row['num_viajes']:.2f}", f"{row['volumen_tn']:.2f}", f"S/ {costo_detalle:,.2f}"
                ))
                
            t_ui = time.time()
            self.log(f"[DEBUG] Renderizado Treeview UI tomó {t_ui - t_calc:.2f}s")

            self.lbl_status.config(text="✅ Optimización Finalizada", fg="green");
            self.btn_optimizar.config(state="normal", text="▶ EJECUTAR OPTIMIZACIÓN")
            self.log("🎉 Proceso completado exitosamente")

            conn.close()

        except Exception as e:
            self.log(f"❌ Error procesando resultados: {e}");
            messagebox.showerror("Error Resultados", f"Error procesando datos:\n{e}")
            self.reactivar_boton()


if __name__ == "__main__":
    root = tk.Tk()
    app = RoqueInterface(root)
    root.mainloop()