import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
from .config import PRESUPUESTO_LIMITE

class RodrikInterface:
    def __init__(self, root, on_reload_data=None, on_verify_constraints=None, on_optimize=None):
        self.root = root
        self.root.title("Sistema de Optimización - RODRIK Transport E.I.R.L.")
        self.root.geometry("1400x900")
        self.root.configure(bg="#e6e6e6")

        # Callbacks
        self.on_reload_data = on_reload_data
        self.on_verify_constraints = on_verify_constraints
        self.on_optimize = on_optimize

        # Inicializar atributos
        self.console = None
        self.lbl_costo_val = None
        self.lbl_presupuesto_val = None
        self.lbl_penalidad_val = None
        self.lbl_viajes_val = None
        self.lbl_servicio_val = None
        self.tree = None

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#e6e6e6")
        style.configure("TNotebook", background="#003366")
        style.configure("TNotebook.Tab", background="#e6e6e6", padding=[10, 5])

        self.configurar_interfaz_visual(root)

    def configurar_interfaz_visual(self, root):
        """Configuración y posicionamiento de widgets y pestañas."""
        # --- HEADER SUPERIOR ---
        header_frame = tk.Frame(root, bg="#003366", pady=15)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="OPTIMIZACIÓN DE TRANSPORTE Y LOGÍSTICA",
                 font=("Arial", 22, "bold"), bg="#003366", fg="white").pack()
        tk.Label(header_frame, text="Modelo de Programación por Metas (LINGO 20 + SQL Server)",
                 font=("Arial", 10), bg="#003366", fg="#cccccc").pack()

        # --- NOTEBOOK (TABS) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.tab_principal = tk.Frame(self.notebook, bg="#e6e6e6")
        self.tab_flota = tk.Frame(self.notebook, bg="#e6e6e6")
        self.tab_tarifario = tk.Frame(self.notebook, bg="#e6e6e6")

        self.notebook.add(self.tab_principal, text="Optimización y Resultados")
        self.notebook.add(self.tab_flota, text="Flota y Compatibilidad")
        self.notebook.add(self.tab_tarifario, text="Tarifario y Faltantes")

        self._setup_tab_principal()
        self._setup_tab_flota()
        self._setup_tab_tarifario()

    # =========================================================================
    # CONFIGURACIÓN DE PESTAÑAS
    # =========================================================================

    def _setup_tab_principal(self):
        main_canvas = tk.Canvas(self.tab_principal, bg="#e6e6e6")
        scrollbar = ttk.Scrollbar(self.tab_principal, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Secciones de Oferta y Demanda
        self.crear_seccion_oferta()
        self.crear_seccion_demanda()

        # 2. Botonera Principal
        btn_frame = tk.Frame(self.scrollable_frame, bg="#e6e6e6", pady=20)
        btn_frame.pack(fill="x", padx=20)

        tk.Button(btn_frame, text="🔄 Recargar Datos SQL", bg="#17a2b8", fg="white", width=20,
                  command=self._handle_reload).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔍 Verificar Restricciones", bg="#6c757d", fg="white", width=20,
                  command=self._handle_verify).pack(side="left", padx=5)

        self.btn_optimizar = tk.Button(btn_frame, text="▶ EJECUTAR OPTIMIZACIÓN", bg="#28a745", fg="white",
                                       font=("Arial", 12, "bold"), width=30, height=2,
                                       command=self._handle_optimize)
        self.btn_optimizar.pack(side="right", padx=20)

        self.lbl_status = tk.Label(btn_frame, text="Estado: Listo", font=("Arial", 11, "italic"), bg="#e6e6e6", fg="#555")
        self.lbl_status.pack(side="right", padx=10)

        # 3. Resumen Ejecutivo (Tarjetas)
        self.resumen_frame = tk.Frame(self.scrollable_frame, bg="#e6e6e6")
        self.resumen_frame.pack(fill="x", padx=20, pady=10)

        self.card_costo = self.crear_tarjeta(self.resumen_frame, "Costo Operativo Real", "S/ 0.00", "#007bff")
        self.card_presupuesto = self.crear_tarjeta(self.resumen_frame, "Presupuesto Límite", f"S/ {PRESUPUESTO_LIMITE:,.2f}", "#28a745")
        self.card_penalidad = self.crear_tarjeta(self.resumen_frame, "Penalidad (Faltantes)", "S/ 0.00", "#dc3545")
        self.card_viajes = self.crear_tarjeta(self.resumen_frame, "Total Viajes", "0", "#17a2b8")
        self.card_servicio = self.crear_tarjeta(self.resumen_frame, "Nivel de Servicio", "0%", "#ffc107")

        self.card_costo.pack(side="left", expand=True, fill="x", padx=5)
        self.card_presupuesto.pack(side="left", expand=True, fill="x", padx=5)
        self.card_penalidad.pack(side="left", expand=True, fill="x", padx=5)
        self.card_viajes.pack(side="left", expand=True, fill="x", padx=5)
        self.card_servicio.pack(side="left", expand=True, fill="x", padx=5)

        # 4. Tabla de Detalles (Treeview)
        lbl_det = tk.Label(self.scrollable_frame, text="Detalle de Envíos Programados",
                           font=("Arial", 12, "bold"), bg="#e6e6e6", anchor="w")
        lbl_det.pack(fill="x", padx=20, pady=(20, 5))

        cols = ("Origen", "Destino", "Camión", "Producto", "Semana", "Viajes (N)", "Volumen (TN)", "Costo (S/)")
        self.tree = ttk.Treeview(self.scrollable_frame, columns=cols, show="headings", height=12)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="x", padx=20, pady=5)

        # 5. Consola de Logs
        lbl_log = tk.Label(self.scrollable_frame, text="Log de Ejecución",
                           font=("Arial", 12, "bold"), bg="#e6e6e6", anchor="w")
        lbl_log.pack(fill="x", padx=20, pady=(10, 5))

        self.console = scrolledtext.ScrolledText(self.scrollable_frame, height=8, bg="#1e1e1e", fg="#00ff00",
                                                 font=("Consolas", 9))
        self.console.pack(fill="x", padx=20, pady=5)

    def _setup_tab_flota(self):
        # 1. Tabla de Camiones
        lbl_camiones = tk.Label(self.tab_flota, text="Catálogo de Camiones (Flota)", font=("Arial", 12, "bold"), bg="#e6e6e6")
        lbl_camiones.pack(fill="x", padx=20, pady=(20, 5))

        cols_cam = ("Tipo de Camión", "Capacidad (TN)", "Especialización", "Costo Fijo (S/)")
        self.tree_camiones = ttk.Treeview(self.tab_flota, columns=cols_cam, show="headings", height=4)
        for col in cols_cam:
            self.tree_camiones.heading(col, text=col)
            self.tree_camiones.column(col, width=200, anchor="center")
        self.tree_camiones.pack(fill="x", padx=20, pady=5)

        # 2. Matriz de Compatibilidad
        lbl_compat = tk.Label(self.tab_flota, text="Compatibilidad Camión - Producto", font=("Arial", 12, "bold"), bg="#e6e6e6")
        lbl_compat.pack(fill="x", padx=20, pady=(20, 5))

        cols_comp = ("Tipo de Camión", "Producto", "Es Válido")
        self.tree_compatibilidad = ttk.Treeview(self.tab_flota, columns=cols_comp, show="headings", height=10)
        for col in cols_comp:
            self.tree_compatibilidad.heading(col, text=col)
            self.tree_compatibilidad.column(col, width=200, anchor="center")
        self.tree_compatibilidad.pack(fill="x", padx=20, pady=5)

    def _setup_tab_tarifario(self):
        # 1. Tabla de Costos Base (Tarifario)
        lbl_tarifario = tk.Label(self.tab_tarifario, text="Tarifario Base (Costo por Viaje)", font=("Arial", 12, "bold"), bg="#e6e6e6")
        lbl_tarifario.pack(fill="x", padx=20, pady=(20, 5))

        cols_tar = ("Origen", "Destino", "Producto", "Costo Base (S/)")
        self.tree_tarifario = ttk.Treeview(self.tab_tarifario, columns=cols_tar, show="headings", height=10)
        for col in cols_tar:
            self.tree_tarifario.heading(col, text=col)
            self.tree_tarifario.column(col, width=200, anchor="center")
        self.tree_tarifario.pack(fill="x", padx=20, pady=5)

        # 2. Tabla de Faltantes (Demanda no Atendida)
        lbl_faltantes = tk.Label(self.tab_tarifario, text="Detalle de Demandas No Atendidas (Faltantes)", font=("Arial", 12, "bold"), bg="#e6e6e6", fg="red")
        lbl_faltantes.pack(fill="x", padx=20, pady=(20, 5))

        cols_falt = ("Destino", "Producto", "Semana", "Cantidad Faltante (TN)")
        self.tree_faltantes = ttk.Treeview(self.tab_tarifario, columns=cols_falt, show="headings", height=8)
        for col in cols_falt:
            self.tree_faltantes.heading(col, text=col)
            self.tree_faltantes.column(col, width=200, anchor="center")
        self.tree_faltantes.pack(fill="x", padx=20, pady=5)

    # =========================================================================
    # HELPERS DE UI
    # =========================================================================

    def crear_tarjeta(self, parent, titulo, valor, color):
        f = tk.Frame(parent, bg="white", bd=1, relief="solid")
        tk.Frame(f, bg=color, height=4).pack(fill="x")
        tk.Label(f, text=titulo, bg="white", fg="#666").pack(pady=(10, 0))
        lbl = tk.Label(f, text=valor, bg="white", font=("Arial", 16, "bold"), fg="#333")
        lbl.pack(pady=(5, 15))

        if titulo == "Costo Operativo Real":
            self.lbl_costo_val = lbl
        elif titulo == "Presupuesto Límite":
            self.lbl_presupuesto_val = lbl
        elif titulo == "Penalidad (Faltantes)":
            self.lbl_penalidad_val = lbl
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
            tk.Label(frame, text=h, bg="#eee", font=("Arial", 8, "bold"), width=15).grid(row=0, column=i, sticky="ew", padx=1)
        self.frame_oferta_grid = frame

    def crear_seccion_demanda(self):
        frame = tk.LabelFrame(self.scrollable_frame, text="DEMANDA SEMANAL (TN)", font=("Arial", 10, "bold"),
                              bg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)
        headers = ["Cliente", "Producto", "Semana 1", "Semana 2", "Semana 3", "Semana 4"]
        for i, h in enumerate(headers):
            tk.Label(frame, text=h, bg="#eee", font=("Arial", 8, "bold"), width=15).grid(row=0, column=i, sticky="ew", padx=1)
        self.frame_demanda_grid = frame

    # --- Callbacks Handlers ---
    def _handle_reload(self):
        if self.on_reload_data:
            self.on_reload_data()

    def _handle_verify(self):
        if self.on_verify_constraints:
            self.on_verify_constraints()

    def _handle_optimize(self):
        if self.on_optimize:
            self.on_optimize()

    # --- Métodos de Actualización UI ---
    def log(self, mensaje):
        if hasattr(self, 'console') and self.console:
            timestamp = time.strftime("%H:%M:%S")
            self.console.insert(tk.END, f"[{timestamp}] {mensaje}\n")
            self.console.see(tk.END)
            self.root.update()
        else:
            print(f"LOG: {mensaje}")

    def update_oferta(self, df_o):
        for widget in self.frame_oferta_grid.grid_slaves():
            if int(widget.grid_info()["row"]) > 0: widget.destroy()
        
        row_idx = 1
        for (org, prod), grupo in df_o.groupby(['nombre_origen', 'nombre_producto']):
            tk.Label(self.frame_oferta_grid, text=org, bg="white").grid(row=row_idx, column=0, sticky="nsew", padx=1)
            tk.Label(self.frame_oferta_grid, text=prod, bg="white").grid(row=row_idx, column=1, sticky="nsew", padx=1)
            for sem in range(1, 5):
                val = grupo[grupo['semana_num'] == sem]['cantidad_tn'].sum()
                e = tk.Entry(self.frame_oferta_grid, justify="center", bg="#f9f9f9")
                e.insert(0, f"{val:.0f}")
                e.grid(row=row_idx, column=sem + 1, sticky="ew", padx=1)
            row_idx += 1

    def update_demanda(self, df_d):
        for widget in self.frame_demanda_grid.grid_slaves():
            if int(widget.grid_info()["row"]) > 0: widget.destroy()
        
        row_idx = 1
        for (dest, prod), grupo in df_d.groupby(['nombre_destino', 'nombre_producto']):
            tk.Label(self.frame_demanda_grid, text=dest, bg="white").grid(row=row_idx, column=0, sticky="nsew", padx=1)
            tk.Label(self.frame_demanda_grid, text=prod, bg="white").grid(row=row_idx, column=1, sticky="nsew", padx=1)
            for sem in range(1, 5):
                val = grupo[grupo['semana_num'] == sem]['cantidad_tn'].sum()
                e = tk.Entry(self.frame_demanda_grid, justify="center", bg="#f9f9f9")
                e.insert(0, f"{val:.0f}")
                e.grid(row=row_idx, column=sem + 1, sticky="ew", padx=1)
            row_idx += 1

    def update_treeview(self, df_res):
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        for _, row in df_res.iterrows():
            costo_detalle = row['costo_total_operativo']
            self.tree.insert("", "end", values=(
                row['nombre_origen'], row['nombre_destino'], row['tipo_camion'], row['nombre_producto'],
                row['semana'], f"{row['num_viajes']:.2f}", f"{row['volumen_tn']:.2f}", f"S/ {costo_detalle:,.2f}"
            ))

    def update_camiones(self, df_cam):
        for i in self.tree_camiones.get_children():
            self.tree_camiones.delete(i)
        for _, row in df_cam.iterrows():
            self.tree_camiones.insert("", "end", values=(
                row['tipo_camion'], f"{row['capacidad_efectiva']:.2f}", row['especializacion'], f"S/ {row['costo_fijo']:.2f}"
            ))

    def update_compatibilidad(self, df_comp):
        for i in self.tree_compatibilidad.get_children():
            self.tree_compatibilidad.delete(i)
        for _, row in df_comp.iterrows():
            estado = "✅ SÍ" if row['es_valido'] == 1 else "❌ NO"
            self.tree_compatibilidad.insert("", "end", values=(
                row['tipo_camion'], row['nombre_producto'], estado
            ))

    def update_tarifario(self, df_tar):
        for i in self.tree_tarifario.get_children():
            self.tree_tarifario.delete(i)
        for _, row in df_tar.iterrows():
            self.tree_tarifario.insert("", "end", values=(
                row['nombre_origen'], row['nombre_destino'], row['nombre_producto'], f"S/ {row['costo_base']:.2f}"
            ))

    def update_faltantes(self, df_falt):
        for i in self.tree_faltantes.get_children():
            self.tree_faltantes.delete(i)
        if df_falt.empty:
            self.tree_faltantes.insert("", "end", values=("---", "---", "---", "No hay demandas no atendidas"))
            return
        
        for _, row in df_falt.iterrows():
            self.tree_faltantes.insert("", "end", values=(
                row['nombre_destino'], row['nombre_producto'], row['semana'], f"{row['cantidad_falta']:.2f}"
            ))

    def update_cards(self, total_costo_operativo, costo_penalidad, total_viajes, servicio_text, servicio_color, presupuesto=PRESUPUESTO_LIMITE):
        self.lbl_costo_val.config(text=f"S/ {total_costo_operativo:,.2f}")
        self.lbl_penalidad_val.config(text=f"S/ {costo_penalidad:,.2f}")
        self.lbl_viajes_val.config(text=f"{int(total_viajes)}")
        self.lbl_servicio_val.config(text=servicio_text, fg=servicio_color)
        self.lbl_presupuesto_val.config(text=f"S/ {presupuesto:,.2f}")

    def set_status(self, text, fg_color="black"):
        self.lbl_status.config(text=text, fg=fg_color)

    def set_button_state(self, state, text=None):
        if text:
            self.btn_optimizar.config(state=state, text=text)
        else:
            self.btn_optimizar.config(state=state)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message)
