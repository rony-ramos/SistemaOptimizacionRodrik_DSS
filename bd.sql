CREATE DATABASE ROQUE_TRANSPORT_OPTIMIZATION;
GO

USE ROQUE_TRANSPORT_OPTIMIZATION;
GO

-- TABLAS MAESTRAS

-- Tabla de ORIGENES
CREATE TABLE ORIGEN (
    id_origen INT IDENTITY(1,1) PRIMARY KEY,
    nombre_origen VARCHAR(80) NOT NULL,
    estado BIT DEFAULT 1
);

-- Tabla de DESTINOS
CREATE TABLE DESTINO (
    id_destino INT IDENTITY(1,1) PRIMARY KEY,
    nombre_destino VARCHAR(80) NOT NULL,
    estado BIT DEFAULT 1
);

-- Tabla de CAMIONES
CREATE TABLE CAMION (
    id_camion INT IDENTITY(1,1) PRIMARY KEY,
    tipo_camion VARCHAR(80) NOT NULL,
    capacidad_efectiva DECIMAL(10,2) NOT NULL,
    especializacion VARCHAR(100) NOT NULL,
    costo_fijo DECIMAL(10,2) DEFAULT 0.00,
    estado BIT DEFAULT 1
);

-- Tabla de PRODUCTOS
CREATE TABLE PRODUCTO (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre_producto VARCHAR(80) NOT NULL,
    estado BIT DEFAULT 1
);

-- Tabla de PERIODOS
CREATE TABLE PERIODO (
    id_periodo INT IDENTITY(1,1) PRIMARY KEY,
    nombre_periodo VARCHAR(50) NOT NULL,
    semana_num INT NOT NULL,
    estado BIT DEFAULT 1
);

-- TABLAS DE DATOS OPERATIVOS

-- Tabla de OFERTA
CREATE TABLE OFERTA (
    id_oferta INT IDENTITY(1,1) PRIMARY KEY,
    id_origen INT NOT NULL,
    id_producto INT NOT NULL,
    id_periodo INT NOT NULL,
    cantidad_tn DECIMAL(10,2) NOT NULL,
    fecha_registro DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (id_origen) REFERENCES ORIGEN(id_origen),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto),
    FOREIGN KEY (id_periodo) REFERENCES PERIODO(id_periodo)
);

-- Tabla de DEMANDA
CREATE TABLE DEMANDA (
    id_demanda INT IDENTITY(1,1) PRIMARY KEY,
    id_destino INT NOT NULL,
    id_producto INT NOT NULL,
    id_periodo INT NOT NULL,
    cantidad_tn DECIMAL(10,2) NOT NULL,
    fecha_registro DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (id_destino) REFERENCES DESTINO(id_destino),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto),
    FOREIGN KEY (id_periodo) REFERENCES PERIODO(id_periodo)
);

-- Tabla de COSTOS
CREATE TABLE COSTO (
    id_costo INT IDENTITY(1,1) PRIMARY KEY,
    id_origen INT NOT NULL,
    id_destino INT NOT NULL,
    id_producto INT NOT NULL,
    costo_aceites DECIMAL(10,2),
    costo_pastas DECIMAL(10,2),
    costo_limpieza DECIMAL(10,2),
    costo_base DECIMAL(10,2),
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (id_origen) REFERENCES ORIGEN(id_origen),
    FOREIGN KEY (id_destino) REFERENCES DESTINO(id_destino),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto)
);

-- Tabla de combinaciones válidas entre camión y producto
CREATE TABLE VALIDA_CAMION_PRODUCTO (
    id_valida INT IDENTITY(1,1) PRIMARY KEY,
    id_camion INT NOT NULL,
    id_producto INT NOT NULL,
    estado BIT DEFAULT 1,
    FOREIGN KEY (id_camion) REFERENCES CAMION(id_camion),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto)
);


CREATE TABLE DISPONIBILIDAD_CAMION (
id_disponibilidad INT IDENTITY(1,1) PRIMARY KEY,
id_camion INT NOT NULL,
id_periodo INT NOT NULL,
cantidad_viajes INT NOT NULL,
estado BIT DEFAULT 1,
FOREIGN KEY (id_camion) REFERENCES CAMION(id_camion),
FOREIGN KEY (id_periodo) REFERENCES PERIODO(id_periodo)
); 

-- INSERCIÓN DE DATOS MAESTROS

-- Insertar ORÍGENES
INSERT INTO ORIGEN (nombre_origen) VALUES
('Alicorp Lurin'),
('Alicorp Huachipa');

-- Insertar DESTINOS
INSERT INTO DESTINO (nombre_destino) VALUES
('Cencosud Huachipa'),
('Supesa Lurin'),
('Tottus Ate'),
('Supesa Punta Negra');

-- Insertar CAMIONES
INSERT INTO CAMION (tipo_camion, capacidad_efectiva, especializacion, costo_fijo) VALUES
('Semi trailer seco', 28.00, 'Carga seca de alto volumen', 150.00),
('Camion Hino furgon cerrado', 16.00, 'Productos empacados y protegidos', 100.00),
('Camion Semi Hino mediano de carga', 12.00, 'Carga mediana y entregas urbanas', 80.00);

-- Insertar PRODUCTOS ALICORP
INSERT INTO PRODUCTO (nombre_producto) VALUES
('Aceites domesticos'),
('Fideos y pastas'),
('Detergentes y productos de limpieza');

-- Insertar PERIODOS
INSERT INTO PERIODO (nombre_periodo, semana_num) VALUES
('Semana 1', 1),
('Semana 2', 2),
('Semana 3', 3),
('Semana 4', 4);

-- INSERCIÓN DE OFERTA
-- Oferta Alicorp Lurin
INSERT INTO OFERTA (id_origen, id_producto, id_periodo, cantidad_tn) VALUES
(1, 1, 1, 1250.0), (1, 1, 2, 1320.0), (1, 1, 3, 1405.0), (1, 1, 4, 1180.0),
(1, 2, 1, 1680.0), (1, 2, 2, 1750.0), (1, 2, 3, 1845.0), (1, 2, 4, 1590.0),
(1, 3, 1, 980.0),  (1, 3, 2, 1045.0), (1, 3, 3, 1120.0), (1, 3, 4, 930.0);

-- Oferta Alicorp Huachipa
INSERT INTO OFERTA (id_origen, id_producto, id_periodo, cantidad_tn) VALUES
(2, 1, 1, 1460.0), (2, 1, 2, 1535.0), (2, 1, 3, 1620.0), (2, 1, 4, 1395.0),
(2, 2, 1, 1890.0), (2, 2, 2, 1985.0), (2, 2, 3, 2070.0), (2, 2, 4, 1765.0),
(2, 3, 1, 1190.0), (2, 3, 2, 1260.0), (2, 3, 3, 1345.0), (2, 3, 4, 1085.0);

-- INSERCIÓN DE DEMANDA

-- Demanda Cencosud Huachipa
INSERT INTO DEMANDA (id_destino, id_producto, id_periodo, cantidad_tn) VALUES
(1, 1, 1, 820.0),  (1, 1, 2, 870.0),  (1, 1, 3, 925.0),  (1, 1, 4, 760.0),
(1, 2, 1, 1040.0), (1, 2, 2, 1110.0), (1, 2, 3, 1185.0), (1, 2, 4, 980.0),
(1, 3, 1, 690.0),  (1, 3, 2, 735.0),  (1, 3, 3, 780.0),  (1, 3, 4, 650.0);

-- Demanda Supesa Lurin
INSERT INTO DEMANDA (id_destino, id_producto, id_periodo, cantidad_tn) VALUES
(2, 1, 1, 640.0),  (2, 1, 2, 690.0),  (2, 1, 3, 735.0),  (2, 1, 4, 610.0),
(2, 2, 1, 880.0),  (2, 2, 2, 940.0),  (2, 2, 3, 995.0),  (2, 2, 4, 810.0),
(2, 3, 1, 520.0),  (2, 3, 2, 570.0),  (2, 3, 3, 615.0),  (2, 3, 4, 490.0);

-- Demanda Tottus Ate
INSERT INTO DEMANDA (id_destino, id_producto, id_periodo, cantidad_tn) VALUES
(3, 1, 1, 710.0),  (3, 1, 2, 755.0),  (3, 1, 3, 810.0),  (3, 1, 4, 670.0),
(3, 2, 1, 970.0),  (3, 2, 2, 1035.0), (3, 2, 3, 1095.0), (3, 2, 4, 900.0),
(3, 3, 1, 610.0),  (3, 3, 2, 655.0),  (3, 3, 3, 700.0),  (3, 3, 4, 575.0);

-- Demanda Supesa Punta Negra
INSERT INTO DEMANDA (id_destino, id_producto, id_periodo, cantidad_tn) VALUES
(4, 1, 1, 540.0),  (4, 1, 2, 580.0),  (4, 1, 3, 620.0),  (4, 1, 4, 515.0),
(4, 2, 1, 680.0),  (4, 2, 2, 730.0),  (4, 2, 3, 775.0),  (4, 2, 4, 640.0),
(4, 3, 1, 350.0),  (4, 3, 2, 390.0),  (4, 3, 3, 420.0),  (4, 3, 4, 300.0);

-- INSERCIÓN DE COSTOS
INSERT INTO COSTO 
(id_origen, id_destino, id_producto, costo_aceites, costo_pastas, costo_limpieza, costo_base) 
VALUES

-- Alicorp Lurin -> Cencosud Huachipa
(1, 1, 1, 1210.0, 1080.0, 1165.0, 1080.0),
(1, 1, 2, 1210.0, 1080.0, 1165.0, 1080.0),
(1, 1, 3, 1210.0, 1080.0, 1165.0, 1080.0),

-- Alicorp Lurin -> Supesa Lurin
(1, 2, 1, 980.0,  890.0,  950.0,  890.0),
(1, 2, 2, 980.0,  890.0,  950.0,  890.0),
(1, 2, 3, 980.0,  890.0,  950.0,  890.0),

-- Alicorp Lurin -> Tottus Ate
(1, 3, 1, 1160.0, 1035.0, 1110.0, 1035.0),
(1, 3, 2, 1160.0, 1035.0, 1110.0, 1035.0),
(1, 3, 3, 1160.0, 1035.0, 1110.0, 1035.0),

-- Alicorp Lurin -> Supesa Punta Negra
(1, 4, 1, 1045.0, 955.0, 1015.0, 955.0),
(1, 4, 2, 1045.0, 955.0, 1015.0, 955.0),
(1, 4, 3, 1045.0, 955.0, 1015.0, 955.0),

-- Alicorp Huachipa -> Cencosud Huachipa
(2, 1, 1, 920.0,  850.0,  895.0,  850.0),
(2, 1, 2, 920.0,  850.0,  895.0,  850.0),
(2, 1, 3, 920.0,  850.0,  895.0,  850.0),

-- Alicorp Huachipa -> Supesa Lurin
(2, 2, 1, 1240.0, 1115.0, 1195.0, 1115.0),
(2, 2, 2, 1240.0, 1115.0, 1195.0, 1115.0),
(2, 2, 3, 1240.0, 1115.0, 1195.0, 1115.0),

-- Alicorp Huachipa -> Tottus Ate
(2, 3, 1, 1015.0, 925.0, 985.0, 925.0),
(2, 3, 2, 1015.0, 925.0, 985.0, 925.0),
(2, 3, 3, 1015.0, 925.0, 985.0, 925.0),

-- Alicorp Huachipa -> Supesa Punta Negra
(2, 4, 1, 1355.0, 1220.0, 1305.0, 1220.0),
(2, 4, 2, 1355.0, 1220.0, 1305.0, 1220.0),
(2, 4, 3, 1355.0, 1220.0, 1305.0, 1220.0);

-- COMBINACIONES VÁLIDAS CAMIÓN - PRODUCTO
INSERT INTO VALIDA_CAMION_PRODUCTO (id_camion, id_producto) VALUES
(1, 1), -- Semi trailer seco - Aceites domésticos
(1, 2), -- Semi trailer seco - Fideos y pastas
(1, 3), -- Semi trailer seco - Detergentes y productos de limpieza

(2, 1), -- Camion Hino furgon cerrado - Aceites domésticos
(2, 2), -- Camion Hino furgon cerrado - Fideos y pastas
(2, 3), -- Camion Hino furgon cerrado - Detergentes y productos de limpieza

(3, 2), -- Camión Semi Hino mediano de carga - Fideos y pastas
(3, 3); -- Camión Semi Hino mediano de carga - Detergentes y productos de limpieza


INSERT INTO DISPONIBILIDAD_CAMION (id_camion, id_periodo, cantidad_viajes) VALUES
(1, 1, 80), (1, 2, 85), (1, 3, 90), (1, 4, 75),
(2, 1, 100), (2, 2, 105), (2, 3, 110), (2, 4, 95),
(3, 1, 70), (3, 2, 75), (3, 3, 80), (3, 4, 65); 
GO

-- =========================================================================
-- VISTAS REQUERIDAS POR LINGO (@ODBC)
-- =========================================================================

-- Lingo lee de aquí los camiones y su capacidad
CREATE VIEW VW_CAMION_ORDENADO AS
SELECT TOP (100) PERCENT 
    tipo_camion, 
    capacidad_efectiva
FROM CAMION
ORDER BY id_camion ASC;
GO

-- Lingo lee de aquí la matriz binaria de compatibilidad Camión-Producto
CREATE VIEW VW_MATRIZ_COMPATIBILIDAD AS
SELECT TOP (100) PERCENT
    c.id_camion,
    p.id_producto,
    CASE WHEN v.id_valida IS NOT NULL THEN 1 ELSE 0 END AS es_valido
FROM CAMION c
CROSS JOIN PRODUCTO p
LEFT JOIN VALIDA_CAMION_PRODUCTO v 
    ON c.id_camion = v.id_camion AND p.id_producto = v.id_producto
ORDER BY c.id_camion ASC, p.id_producto ASC;
GO


-- =========================================================================
-- TABLAS DE RESULTADOS DONDE LINGO EXPORTARÁ (@ODBC)
-- =========================================================================

-- Donde LINGO exporta la variable "N" (Número de viajes)
CREATE TABLE RESULTADOS_OPTIMIZACION (
    nombre_origen VARCHAR(80),
    nombre_destino VARCHAR(80),
    tipo_camion VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50), 
    num_viajes DECIMAL(10,2)
);
GO

-- Donde LINGO exporta la variable "FALTA" (Demanda insatisfecha)
CREATE TABLE RESULTADOS_FALTA (
    nombre_destino VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50),
    cantidad_falta DECIMAL(10,2)
);
GO

-- Donde LINGO exporta la variable "X" (Cantidad de toneladas)
CREATE TABLE RESULTADOS_X (
    nombre_origen VARCHAR(80),
    nombre_destino VARCHAR(80),
    tipo_camion VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50),
    cantidad_tn DECIMAL(10,2)
);
GO

-- =========================================================================
-- PRE-LLENADO DE TABLAS PARA EXPORTACIÓN DE LINGO
-- Lingo requiere que las tablas ya tengan las filas creadas para hacer UPDATE
-- =========================================================================

-- Llenar RESULTADOS_FALTA (48 filas = 4 Destinos x 3 Productos x 4 Periodos)
INSERT INTO RESULTADOS_FALTA (nombre_destino, nombre_producto, semana, cantidad_falta)
SELECT d.nombre_destino, p.nombre_producto, pe.nombre_periodo, 0.0
FROM DESTINO d
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY d.id_destino, p.id_producto, pe.id_periodo;
GO

-- Llenar RESULTADOS_OPTIMIZACION (288 filas = 2x4x3x3x4)
INSERT INTO RESULTADOS_OPTIMIZACION (nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, num_viajes)
SELECT o.nombre_origen, d.nombre_destino, c.tipo_camion, p.nombre_producto, pe.nombre_periodo, 0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;
GO

-- Llenar RESULTADOS_X (288 filas = 2x4x3x3x4)
INSERT INTO RESULTADOS_X (nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, cantidad_tn)
SELECT o.nombre_origen, d.nombre_destino, c.tipo_camion, p.nombre_producto, pe.nombre_periodo, 0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;
GO


USE ROQUE_TRANSPORT_OPTIMIZATION;
GO

-- 1. Vaciamos las tablas para evitar duplicados
TRUNCATE TABLE RESULTADOS_FALTA;
TRUNCATE TABLE RESULTADOS_OPTIMIZACION;
TRUNCATE TABLE RESULTADOS_X;
GO

-- 2. Llenamos RESULTADOS_FALTA (48 filas exactas)
INSERT INTO RESULTADOS_FALTA (nombre_destino, nombre_producto, semana, cantidad_falta)
SELECT d.nombre_destino, p.nombre_producto, pe.nombre_periodo, 0.0
FROM DESTINO d
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY d.id_destino, p.id_producto, pe.id_periodo;

-- 3. Llenamos RESULTADOS_OPTIMIZACION (288 filas exactas)
INSERT INTO RESULTADOS_OPTIMIZACION (nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, num_viajes)
SELECT o.nombre_origen, d.nombre_destino, c.tipo_camion, p.nombre_producto, pe.nombre_periodo, 0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;

-- 4. Llenamos RESULTADOS_X (288 filas exactas)
INSERT INTO RESULTADOS_X (nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, cantidad_tn)
SELECT o.nombre_origen, d.nombre_destino, c.tipo_camion, p.nombre_producto, pe.nombre_periodo, 0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;
GO
