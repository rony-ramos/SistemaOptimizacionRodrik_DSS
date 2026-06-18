# Sistema de Optimización - RODRIK Transport E.I.R.L

Este proyecto es una aplicación de escritorio desarrollada en Python que se integra con el motor de optimización LINGO y una base de datos SQL Server para resolver problemas de ruteo, asignación de flota y optimización de costos para RODRIK Transport E.I.R.L.

## Arquitectura del Proyecto

El sistema está compuesto por tres componentes principales:
1. **Base de Datos (SQL Server)**: Almacena los parámetros del problema (oferta, demanda, flota, costos) y recibe los resultados de la optimización (`bd.sql`).
2. **Modelo Matemático (LINGO)**: Un script de LINGO (`MODELO LINGO.lng` o `.lg4`) que se conecta a SQL Server vía ODBC para importar parámetros, resolver el modelo de optimización lineal/entera y exportar los resultados de vuelta a la base de datos.
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
- Por defecto, `app_rodrik.py` está apuntando al servidor `DESKTOP-KDQUSML\SQLEXPRESS`.
- Abre `app_rodrik.py` y edita la constante `SERVER_SQL` (alrededor de la línea 56) si el nombre de tu servidor local SQL es distinto.
- **Importante para LINGO**: Tu sistema Windows debe tener configurado un DSN ODBC, o bien el modelo LINGO usará una cadena de conexión directa. Asegúrate de que LINGO tenga permisos para autenticarse (usa *Trusted_Connection* por defecto).
- El nombre del ODBC en windows debe tener el nombre de `RODRIK_ODBC`. Para configurarlo en Windows, ve a "Fuentes de datos ODBC" (busca en el buscador de Windows) y configura un nuevo DSN de 32 bits (ya que LINGO es de 32 bits) con el nombre `RODRIK_ODBC` y apunta a tu servidor SQL Server y selecciona por defecto la base de datos `RODRIK_TRANSPORT_OPTIMIZATION` en la configuración del ODBC.

### 3. Ejecutar la Aplicación
Inicia la interfaz ejecutando:
```bash
python app_rodrik.py
```

### 4. Características de Resiliencia y Rendimiento
- **Búsqueda Automática de LINGO**: El script de Python detectará automáticamente dónde está instalado LINGO en tu PC (priorizando el motor de consola `RunLingo.exe` para que el cálculo se haga en milisegundos de forma invisible).
- **Detección del Modelo**: El código buscará automáticamente cualquier archivo con el nombre `MODELO LINGO.lng` o `.lg4` en la misma carpeta del script o en la carpeta superior, facilitando compartir el proyecto entre distintos miembros del equipo sin que se rompan las rutas de los archivos.

## Uso del Sistema
Una vez abierta la interfaz gráfica:
1. Haz clic en **▶ EJECUTAR OPTIMIZACIÓN**.
2. Podrás ver los logs de procesamiento en el cuadro negro inferior, con tiempos de respuesta exactos de la conexión SQL y la solución matemática.
3. Al terminar (1-2 segundos), verás en pantalla la tabla con el ruteo óptimo, costo total operativo y penalidades, si las hubiera.
