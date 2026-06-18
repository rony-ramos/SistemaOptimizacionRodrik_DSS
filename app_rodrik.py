import tkinter as tk
from threading import Thread
import pyodbc
import time
import subprocess
import warnings

# Ignorar advertencias de compatibilidad de Pandas
warnings.filterwarnings("ignore")

from modules.config import LINGO_EXE_PATH, MODELO_PATH, CONN_STR
import modules.database as db
import modules.optimization as opt
from modules.ui import RodrikInterface

class Orchestrator:
    def __init__(self, root):
        self.root = root
        self.ui = RodrikInterface(
            root, 
            on_reload_data=self.reload_data, 
            on_verify_constraints=self.verify_constraints, 
            on_optimize=self.start_optimization
        )
        
        self.ui.log("Sistema inicializado y conectado a SQL.")
        self.ui.log(f"Modelo LINGO: {MODELO_PATH}")
        self.test_db_connection()
        self.reload_data()

    def test_db_connection(self):
        success, msg = db.test_connection()
        self.ui.log(msg)
        if not success:
            self.ui.show_error("Error BD", msg)

    def reload_data(self):
        try:
            self.ui.log("Cargando datos de oferta y demanda...")
            df_o = db.fetch_oferta()
            df_d = db.fetch_demanda()
            self.ui.update_oferta(df_o)
            self.ui.update_demanda(df_d)
            self.ui.log("✅ Datos cargados correctamente")
        except Exception as e:
            self.ui.log(f"❌ Error cargando inputs: {e}")
            self.ui.show_error("Error", f"Error cargando datos:\n{e}")

    def verify_constraints(self):
        try:
            self.ui.log("Verificando restricciones del modelo...")
            t0 = time.time()
            
            df_compat = db.check_compatibilidad()
            if not df_compat.empty:
                self.ui.log("❌ Violaciones de compatibilidad camión-producto encontradas:")
                for _, row in df_compat.iterrows():
                    self.ui.log(f"   - {row['tipo_camion']} transportando {row['nombre_producto']}: {row['total_viajes']:.2f} viajes")
                self.ui.show_warning("Restricción violada", "Se encontraron combinaciones no permitidas entre camión y producto.")
            else:
                self.ui.log("✅ No se encontraron violaciones de compatibilidad camión-producto.")

            df_disp = db.check_disponibilidad()
            if not df_disp.empty:
                self.ui.log("❌ Violaciones de disponibilidad máxima de viajes encontradas:")
                for _, row in df_disp.iterrows():
                    self.ui.log(f"   - {row['tipo_camion']} en {row['nombre_periodo']}: {row['viajes_asignados']:.2f} viajes asignados / {row['viajes_disponibles']} disponibles")
                self.ui.show_warning("Restricción violada", "Se asignaron más viajes de los disponibles para uno o más camiones.")
            else:
                self.ui.log("✅ No se encontraron violaciones de disponibilidad de camiones.")

            t1 = time.time()
            self.ui.log(f"[DEBUG] verificar_restricciones tomó {t1 - t0:.2f}s")
        except Exception as e:
            self.ui.log(f"❌ Error verificando restricciones: {e}")

    def start_optimization(self):
        self.ui.set_button_state("disabled", "PROCESANDO...")
        self.ui.set_status("⏳ Ejecutando Motor LINGO...", "#e67e22")
        self.ui.log("Iniciando optimización con LINGO.")

        Thread(target=self.run_lingo_thread, daemon=True).start()

    def run_lingo_thread(self):
        try:
            self.ui.log("Verificando archivos y rutas de LINGO...")
            proceso, t_ejecucion = opt.run_lingo_model(LINGO_EXE_PATH, MODELO_PATH)
            self.ui.log(f"[DEBUG] ⏳ Tiempo de ejecución LINGO (subprocess): {t_ejecucion:.2f}s")

            if proceso.returncode == 0:
                self.ui.log("✅ LINGO ejecutado exitosamente")
                self.root.after(0, self.process_results)
            else:
                self.ui.log(f"❌ LINGO terminó con errores (Código: {proceso.returncode})")
                self.ui.log(f"Error detallado: {proceso.stderr[:500]}...")
                self.root.after(0, lambda: self.ui.show_error("Error LINGO", proceso.stderr))
                self.root.after(0, self.reactivate_button)
        except subprocess.TimeoutExpired:
            self.ui.log("❌ LINGO excedió el tiempo límite (5 minutos)")
            self.root.after(0, lambda: self.ui.show_error("Timeout", "LINGO excedió el tiempo límite"))
            self.root.after(0, self.reactivate_button)
        except Exception as e:
            self.ui.log(f"❌ Error ejecutando LINGO: {e}")
            self.root.after(0, lambda: self.ui.show_error("Error LINGO", str(e)))
            self.root.after(0, self.reactivate_button)

    def reactivate_button(self):
        self.ui.set_button_state("normal", "▶ EJECUTAR OPTIMIZACIÓN")
        self.ui.set_status("❌ Error en ejecución", "red")

    def process_results(self):
        self.ui.set_status("📥 Procesando resultados...", "blue")
        self.ui.log("Leyendo resultados de la base de datos...")
        t_inicio_sql = time.time()

        try:
            conn = pyodbc.connect(CONN_STR)
            t_conn = time.time()
            self.ui.log(f"[DEBUG] Conexión SQL tomó {t_conn - t_inicio_sql:.2f}s")

            df_res = db.fetch_resultados_optimizacion(conn)
            t_query1 = time.time()
            self.ui.log(f"[DEBUG] Lectura df_res tomó {t_query1 - t_conn:.2f}s")

            if df_res.empty:
                self.ui.log("⚠️ No se encontraron envíos programados")
                self.ui.set_status("⚠️ Sin envíos.", "orange")
                self.reactivate_button()
                conn.close()
                return

            self.ui.log(f"📊 Encontrados {len(df_res)} registros de envíos")

            df_falta = db.fetch_faltantes(conn)
            demanda_total_df = db.fetch_demanda_total(conn)

            df_res, total_costo, total_viajes, total_volumen, demanda_total = opt.calculate_metrics(
                df_res, df_falta, demanda_total_df
            )
            
            t_calc = time.time()
            self.ui.log(f"[DEBUG] calcular_metricas_y_costo tomó {t_calc - t_query1:.2f}s")

            df_compat = db.check_compatibilidad(conn)
            if not df_compat.empty:
                self.ui.log("❌ Violaciones de compatibilidad camión-producto encontradas.")
            
            df_disp = db.check_disponibilidad(conn)
            if not df_disp.empty:
                self.ui.log("❌ Violaciones de disponibilidad máxima de viajes encontradas.")

            # Actualizar Interfaz
            servicio = 0
            servicio_text = "0.00%"
            servicio_color = "black"

            if demanda_total > 0:
                servicio = (total_volumen / demanda_total) * 100
                servicio_text = f"{servicio:.2f}%"

                if servicio < 95.0 or servicio > 105.0:
                    servicio_color = "red"
                    self.ui.log(f"⚠️ Nivel de servicio: {servicio:.2f}% (Fuera de rango)")
                else:
                    servicio_color = "green"
                    self.ui.log(f"✅ Nivel de servicio óptimo: {servicio:.2f}%")

            self.ui.update_cards(total_costo, total_viajes, servicio_text, servicio_color)
            self.ui.update_treeview(df_res)
            
            t_ui = time.time()
            self.ui.log(f"[DEBUG] Renderizado Treeview UI tomó {t_ui - t_calc:.2f}s")

            self.ui.set_status("✅ Optimización Finalizada", "green")
            self.ui.set_button_state("normal", "▶ EJECUTAR OPTIMIZACIÓN")
            self.ui.log("🎉 Proceso completado exitosamente")

            conn.close()

        except Exception as e:
            self.ui.log(f"❌ Error procesando resultados: {e}")
            self.ui.show_error("Error Resultados", f"Error procesando datos:\n{e}")
            self.reactivate_button()

if __name__ == "__main__":
    root = tk.Tk()
    app = Orchestrator(root)
    root.mainloop()
