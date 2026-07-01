# Sistema de Optimización - RODRIK Transport E.I.R.L

Este proyecto es una aplicación de escritorio desarrollada en Python que se integra con el motor de optimización LINGO y una base de datos SQL Server para resolver problemas de ruteo, asignación de flota y optimización de costos para RODRIK Transport E.I.R.L.

## Arquitectura del Proyecto

El sistema está compuesto por tres componentes principales:
1. **Base de Datos (SQL Server)**: Almacena los parámetros del problema (oferta, demanda, flota, costos) y recibe los resultados de la optimización (`bd.sql`).
2. **Modelo Matemático (LINGO)**: Un script de LINGO (`lingo.lng`) que se conecta a SQL Server vía ODBC para importar parámetros, resolver el modelo de optimización lineal/entera y exportar los resultados de vuelta a la base de datos.
3. **Interfaz de Usuario (Python)**: Una aplicación visual (`app_rodrik.py`) desarrollada con Tkinter que coordina el proceso: ejecuta LINGO silenciosamente en segundo plano, lee los resultados en la base de datos y los presenta al usuario de forma amigable junto con métricas financieras.

## Requisitos Previos

- **Python 3.8+**
- **LINGO (versión 64-bit)** instalado en Windows (usualmente en `C:\LINGO64_21` o similar).
- **Microsoft SQL Server** (local o express).
- **Controlador ODBC** para SQL Server.

## Guía de Instalación (Entorno Local)

Para ejecutar este proyecto en tu computadora, sigue estos pasos:

### 1. Clonar el Repositorio
Abre tu terminal y clona este proyecto:
```bash
git clone https://github.com/rony-ramos/Sistema-de-Optimizaci-n---RODRIK Transport E.I.R.L..git
cd Sistema-de-Optimizaci-n---RODRIK-Transport-E.I.R.L./IOP2
```

### 2. Crear un Entorno Virtual (Recomendado)
Para no afectar otras instalaciones de Python en tu sistema, crea un entorno virtual (venv):
```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual (En Windows)
venv\Scripts\activate
```
*(Nota: Cuando el entorno esté activo, verás `(venv)` al inicio de tu línea de comandos).*

### 3. Instalar Dependencias
Con el entorno virtual activado, instala todas las librerías necesarias ejecutando:
```bash
pip install -r requirements.txt
```
*(Tkinter, la librería gráfica utilizada para la interfaz, ya viene incluida en la instalación estándar de Python en Windows, por lo que no necesita ser instalada con pip).*

## Configuración y Ejecución

### 1. Preparar la Base de Datos
- Abre tu gestor de base de datos (SSMS o Azure Data Studio).
- Ejecuta todo el script `bd.sql` en tu servidor SQL. Esto creará la base de datos `RODRIK_TRANSPORT_OPTIMIZATION`, las tablas, insertará los datos maestros (destinos, orígenes, camiones) e incluirá el *pre-llenado* de las tablas de resultados requerido por LINGO.
- Si necesitas reiniciar las tablas de exportación en algún momento, el propio script cuenta con un bloque al final para limpiar y repoblar las 48/288 filas necesarias.

### 2. Configurar la Conexión ODBC
- Por defecto, el sistema está apuntando al servidor `DESKTOP-KDQUSML\SQLEXPRESS`.
- Abre `modules/config.py` y edita la constante `SERVER_SQL` (alrededor de la línea 8) si el nombre de tu servidor local SQL es distinto.
- **Importante para LINGO**: Tu sistema Windows debe tener configurado un DSN ODBC. Asegúrate de que LINGO tenga permisos para autenticarse (usa *Trusted_Connection* por defecto).
- El nombre del ODBC en Windows debe ser `RODRIK_ODBC`. Para configurarlo en Windows:
  1. Abre la herramienta **Orígenes de datos ODBC (64 bits)** en el Panel de Control de Windows (ya que tu instalación de LINGO64 es de 64 bits).
  2. Ve a la pestaña **DSN de sistema** o **DSN de usuario**.
  3. Agrega un nuevo origen de datos con el nombre `RODRIK_ODBC` apuntando a tu instancia de SQL Server.
  4. Selecciona la base de datos `RODRIK_TRANSPORT_OPTIMIZATION` por defecto en la ventana de configuración del DSN.

### 3. Ejecutar la Aplicación
Inicia la interfaz ejecutando:
```bash
python app_rodrik.py
```

### 4. Características de Resiliencia y Rendimiento
- **Búsqueda Automática de LINGO**: El script de Python detectará automáticamente dónde está instalado LINGO en tu PC (priorizando el motor de consola `RunLingo.exe` para que el cálculo se haga en milisegundos de forma invisible).
- **Detección del Modelo**: El código buscará automáticamente cualquier archivo con extensión `.lng` (como `lingo.lng`) en la misma carpeta del script o en la carpeta superior, facilitando compartir el proyecto entre distintos miembros del equipo sin que se rompan las rutas de los archivos.

## Configuración de Optimización y Parámetros Avanzados

El modelo incluye varias mejoras avanzadas de optimización y lógica para asegurar un rendimiento de nivel empresarial:

### 1. Restricción de Presupuesto Dinámico
Se ha implementado una restricción para limitar el costo de transporte operacional a un presupuesto máximo establecido en LINGO:
* **En LINGO (`lingo.lng`)**: Se define una constante `PRESUPUESTO` en la sección `DATA` (ej. `PRESUPUESTO = 1200000;`) y se aplica la restricción `@SUM(RUTA_CAMION_PERIODO(O, D, C, K, P): COSTO_VIAJE(O, D, K) * X(O, D, C, K, P) ) <= PRESUPUESTO;`.
* **En Python (`modules/config.py`)**: El script lee dinámicamente el valor de `PRESUPUESTO` desde el archivo de LINGO usando expresiones regulares. De esta forma, cualquier cambio realizado en LINGO se refleja automáticamente en la interfaz sin necesidad de duplicar configuraciones.

### 2. Sintonización del Coeficiente Big-M (`M`)
El coeficiente Big-M usado en la activación de rutas (`N <= M * Y`) se ha reducido de `10000` a `400` en LINGO:
* **Razón**: La disponibilidad semanal máxima de viajes de cualquier camión en la base de datos es de 330. Un valor de `M = 400` es matemáticamente seguro ya que nunca limitará una solución real, pero estrecha de forma drástica las cotas matemáticas (relajación lineal), acelerando enormemente la velocidad de resolución en el resolvedor MIP.

### 3. Criterio de Parada y Tolerancia (`IPTOLR`)
Al activar la restricción de presupuesto, el modelo entero mixto se vuelve muy ajustado en su frontera de factibilidad, lo que provoca que LINGO intente demostrar la optimización absoluta (0.00% de gap) tardando varios minutos.
* **Solución**: En el script de ejecución `run_cmd.ltf` y el archivo de pruebas `test_lingo_results.py`, se configura el parámetro **`SET IPTOLR 0.001`**.
* **Impacto**: Esto establece la tolerancia de optimalidad relativa (MIP Gap) en **0.1%**. En cuanto LINGO encuentra una solución factible con un margen de error menor al 0.1% respecto al límite teórico, detiene la búsqueda y guarda los resultados en el acto. Esto reduce el tiempo de ejecución en entornos complejos de minutos a **pocos segundos**.

## Uso del Sistema
Una vez abierta la interfaz gráfica:
1. Haz clic en **▶ EJECUTAR OPTIMIZACIÓN**.
2. Podrás ver los logs de procesamiento en el cuadro negro inferior, con tiempos de respuesta exactos de la conexión SQL y la solución matemática.
3. Al terminar (pocos segundos), verás en pantalla la tabla con el ruteo óptimo, costo total operativo, presupuesto límite y penalidades por faltantes, si las hubiera.
