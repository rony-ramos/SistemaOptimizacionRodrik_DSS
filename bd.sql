CREATE DATABASE RODRIK_TRANSPORT_OPTIMIZATION;
GO

USE RODRIK_TRANSPORT_OPTIMIZATION;
GO

-- ============================================================
-- TABLAS MAESTRAS
-- ============================================================

CREATE TABLE ORIGEN (
    id_origen INT IDENTITY(1,1) PRIMARY KEY,
    nombre_origen VARCHAR(80) NOT NULL,
    estado BIT DEFAULT 1
);

CREATE TABLE DESTINO (
    id_destino INT IDENTITY(1,1) PRIMARY KEY,
    nombre_destino VARCHAR(80) NOT NULL,
    estado BIT DEFAULT 1
);

CREATE TABLE CAMION (
    id_camion INT IDENTITY(1,1) PRIMARY KEY,
    tipo_camion VARCHAR(80) NOT NULL,
    capacidad_efectiva DECIMAL(10,2) NOT NULL,
    especializacion VARCHAR(100) NOT NULL,
    costo_fijo DECIMAL(10,2) DEFAULT 0.00,
    estado BIT DEFAULT 1
);

CREATE TABLE PRODUCTO (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre_producto VARCHAR(80) NOT NULL,
    lote_minimo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    estado BIT DEFAULT 1
);

CREATE TABLE PERIODO (
    id_periodo INT IDENTITY(1,1) PRIMARY KEY,
    nombre_periodo VARCHAR(50) NOT NULL,
    semana_num INT NOT NULL,
    estado BIT DEFAULT 1
);

-- ============================================================
-- TABLAS OPERATIVAS
-- ============================================================

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

CREATE TABLE COSTO (
    id_costo INT IDENTITY(1,1) PRIMARY KEY,
    id_origen INT NOT NULL,
    id_destino INT NOT NULL,
    id_producto INT NOT NULL,
    costo_base DECIMAL(10,2) NOT NULL,
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (id_origen) REFERENCES ORIGEN(id_origen),
    FOREIGN KEY (id_destino) REFERENCES DESTINO(id_destino),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto)
);

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

-- ============================================================
-- NUEVAS TABLAS PARA INVENTARIO Y COSTOS POR RANGO
-- ============================================================

CREATE TABLE INVENTARIO_MINIMO (
    id_inventario INT IDENTITY(1,1) PRIMARY KEY,
    id_origen INT NOT NULL,
    id_producto INT NOT NULL,
    id_periodo INT NOT NULL,
    cantidad_minima DECIMAL(10,2) NOT NULL,
    estado BIT DEFAULT 1,
    FOREIGN KEY (id_origen) REFERENCES ORIGEN(id_origen),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto),
    FOREIGN KEY (id_periodo) REFERENCES PERIODO(id_periodo)
);

CREATE TABLE RANGO_COSTO (
    id_rango INT IDENTITY(1,1) PRIMARY KEY,
    nombre_rango VARCHAR(80) NOT NULL,
    limite_inferior DECIMAL(10,2) NOT NULL,
    limite_superior DECIMAL(10,2) NOT NULL,
    estado BIT DEFAULT 1
);

CREATE TABLE COSTO_RANGO (
    id_costo_rango INT IDENTITY(1,1) PRIMARY KEY,
    id_origen INT NOT NULL,
    id_destino INT NOT NULL,
    id_producto INT NOT NULL,
    id_rango INT NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    estado BIT DEFAULT 1,
    FOREIGN KEY (id_origen) REFERENCES ORIGEN(id_origen),
    FOREIGN KEY (id_destino) REFERENCES DESTINO(id_destino),
    FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto),
    FOREIGN KEY (id_rango) REFERENCES RANGO_COSTO(id_rango)
);

-- ============================================================
-- DATOS MAESTROS
-- ============================================================

INSERT INTO ORIGEN (nombre_origen) VALUES
('Alicorp Lurin'),
('Alicorp Huachipa');

INSERT INTO DESTINO (nombre_destino) VALUES
('Cencosud Huachipa'),
('Supesa Lurin'),
('Tottus Ate'),
('Supesa Punta Negra');

INSERT INTO CAMION (tipo_camion, capacidad_efectiva, especializacion, costo_fijo) VALUES
('Semi trailer seco', 28.00, 'Carga seca de alto volumen', 150.00),
('Camion Hino furgon cerrado', 16.00, 'Productos empacados y protegidos', 100.00),
('Camion Semi Hino mediano de carga', 12.00, 'Carga mediana y entregas urbanas', 80.00);

INSERT INTO PRODUCTO (nombre_producto, lote_minimo) VALUES
('Aceites domesticos', 20.00),
('Fideos y pastas', 15.00),
('Detergentes y productos de limpieza', 10.00);

INSERT INTO PERIODO (nombre_periodo, semana_num) VALUES
('Semana 1', 1),
('Semana 2', 2),
('Semana 3', 3),
('Semana 4', 4);

-- ============================================================
-- OFERTA
-- ============================================================

INSERT INTO OFERTA (id_origen, id_producto, id_periodo, cantidad_tn) VALUES
(1, 1, 1, 1250.0), (1, 1, 2, 1320.0), (1, 1, 3, 1405.0), (1, 1, 4, 1180.0),
(1, 2, 1, 1680.0), (1, 2, 2, 1750.0), (1, 2, 3, 1845.0), (1, 2, 4, 1590.0),
(1, 3, 1, 980.0),  (1, 3, 2, 1045.0), (1, 3, 3, 1120.0), (1, 3, 4, 930.0),

(2, 1, 1, 1460.0), (2, 1, 2, 1535.0), (2, 1, 3, 1620.0), (2, 1, 4, 1395.0),
(2, 2, 1, 1890.0), (2, 2, 2, 1985.0), (2, 2, 3, 2070.0), (2, 2, 4, 1765.0),
(2, 3, 1, 1190.0), (2, 3, 2, 1260.0), (2, 3, 3, 1345.0), (2, 3, 4, 1085.0);

-- ============================================================
-- DEMANDA
-- ============================================================

INSERT INTO DEMANDA (id_destino, id_producto, id_periodo, cantidad_tn) VALUES
(1, 1, 1, 820.0),  (1, 1, 2, 870.0),  (1, 1, 3, 925.0),  (1, 1, 4, 760.0),
(1, 2, 1, 1040.0), (1, 2, 2, 1110.0), (1, 2, 3, 1185.0), (1, 2, 4, 980.0),
(1, 3, 1, 690.0),  (1, 3, 2, 735.0),  (1, 3, 3, 780.0),  (1, 3, 4, 650.0),

(2, 1, 1, 640.0),  (2, 1, 2, 690.0),  (2, 1, 3, 735.0),  (2, 1, 4, 610.0),
(2, 2, 1, 880.0),  (2, 2, 2, 940.0),  (2, 2, 3, 995.0),  (2, 2, 4, 810.0),
(2, 3, 1, 520.0),  (2, 3, 2, 570.0),  (2, 3, 3, 615.0),  (2, 3, 4, 490.0),

(3, 1, 1, 710.0),  (3, 1, 2, 755.0),  (3, 1, 3, 810.0),  (3, 1, 4, 670.0),
(3, 2, 1, 970.0),  (3, 2, 2, 1035.0), (3, 2, 3, 1095.0), (3, 2, 4, 900.0),
(3, 3, 1, 610.0),  (3, 3, 2, 655.0),  (3, 3, 3, 700.0),  (3, 3, 4, 575.0),

(4, 1, 1, 540.0),  (4, 1, 2, 580.0),  (4, 1, 3, 620.0),  (4, 1, 4, 515.0),
(4, 2, 1, 680.0),  (4, 2, 2, 730.0),  (4, 2, 3, 775.0),  (4, 2, 4, 640.0),
(4, 3, 1, 350.0),  (4, 3, 2, 390.0),  (4, 3, 3, 420.0),  (4, 3, 4, 300.0);

-- ============================================================
-- COSTOS BASE
-- ============================================================

INSERT INTO COSTO (id_origen, id_destino, id_producto, costo_base) VALUES
(1, 1, 1, 1210.0), (1, 1, 2, 1080.0), (1, 1, 3, 1165.0),
(1, 2, 1, 980.0),  (1, 2, 2, 890.0),  (1, 2, 3, 950.0),
(1, 3, 1, 1160.0), (1, 3, 2, 1035.0), (1, 3, 3, 1110.0),
(1, 4, 1, 1045.0), (1, 4, 2, 955.0),  (1, 4, 3, 1015.0),

(2, 1, 1, 920.0),  (2, 1, 2, 850.0),  (2, 1, 3, 895.0),
(2, 2, 1, 1240.0), (2, 2, 2, 1115.0), (2, 2, 3, 1195.0),
(2, 3, 1, 1015.0), (2, 3, 2, 925.0),  (2, 3, 3, 985.0),
(2, 4, 1, 1355.0), (2, 4, 2, 1220.0), (2, 4, 3, 1305.0);

-- ============================================================
-- COMPATIBILIDAD CAMIÓN - PRODUCTO
-- ============================================================

INSERT INTO VALIDA_CAMION_PRODUCTO (id_camion, id_producto) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 1),
(2, 2),
(2, 3),
(3, 2),
(3, 3);

-- ============================================================
-- DISPONIBILIDAD DE VIAJES POR CAMIÓN Y SEMANA
-- ============================================================

INSERT INTO DISPONIBILIDAD_CAMION (id_camion, id_periodo, cantidad_viajes) VALUES
-- Semi trailer seco
(1, 1, 110), (1, 2, 115), (1, 3, 120), (1, 4, 105),

-- Camion Hino furgon cerrado
(2, 1, 130), (2, 2, 135), (2, 3, 140), (2, 4, 125),

-- Camion Semi Hino mediano de carga
(3, 1, 100), (3, 2, 105), (3, 3, 110), (3, 4, 95);
-- ============================================================
-- INVENTARIO MÍNIMO
-- Se considera 5% de la oferta como inventario de seguridad
-- ============================================================

INSERT INTO INVENTARIO_MINIMO (id_origen, id_producto, id_periodo, cantidad_minima)
SELECT 
    id_origen,
    id_producto,
    id_periodo,
    ROUND(cantidad_tn * 0.05, 2)
FROM OFERTA;

-- ============================================================
-- RANGOS DE COSTO
-- ============================================================

INSERT INTO RANGO_COSTO (nombre_rango, limite_inferior, limite_superior) VALUES
('Rango 1 - Bajo volumen', 0.00, 500.00),
('Rango 2 - Volumen medio', 500.01, 1000.00),
('Rango 3 - Alto volumen', 1000.01, 10000.00);

-- ============================================================
-- COSTOS POR RANGO
-- Rango 1: costo base
-- Rango 2: 5% de descuento
-- Rango 3: 10% de descuento
-- ============================================================

INSERT INTO COSTO_RANGO 
(id_origen, id_destino, id_producto, id_rango, costo_unitario)
SELECT 
    c.id_origen,
    c.id_destino,
    c.id_producto,
    r.id_rango,
    ROUND(
        c.costo_base *
        CASE 
            WHEN r.id_rango = 1 THEN 1.00
            WHEN r.id_rango = 2 THEN 0.95
            WHEN r.id_rango = 3 THEN 0.90
        END, 2
    ) AS costo_unitario
FROM COSTO c
CROSS JOIN RANGO_COSTO r;

-- ============================================================
-- TABLAS DE RESULTADOS DONDE LINGO EXPORTARÁ
-- ============================================================

CREATE TABLE RESULTADOS_OPTIMIZACION (
    nombre_origen VARCHAR(80),
    nombre_destino VARCHAR(80),
    tipo_camion VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50),
    num_viajes DECIMAL(10,2)
);

CREATE TABLE RESULTADOS_FALTA (
    nombre_destino VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50),
    cantidad_falta DECIMAL(10,2)
);

CREATE TABLE RESULTADOS_X (
    nombre_origen VARCHAR(80),
    nombre_destino VARCHAR(80),
    tipo_camion VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50),
    cantidad_tn DECIMAL(10,2)
);

-- Opcional: si luego deseas exportar el volumen asignado por rango
CREATE TABLE RESULTADOS_RANGO (
    nombre_origen VARCHAR(80),
    nombre_destino VARCHAR(80),
    tipo_camion VARCHAR(80),
    nombre_producto VARCHAR(80),
    semana VARCHAR(50),
    nombre_rango VARCHAR(80),
    cantidad_tn DECIMAL(10,2)
);

-- ============================================================
-- PRELLENADO DE TABLAS DE RESULTADOS
-- ============================================================

INSERT INTO RESULTADOS_FALTA (nombre_destino, nombre_producto, semana, cantidad_falta)
SELECT 
    d.nombre_destino,
    p.nombre_producto,
    pe.nombre_periodo,
    0.0
FROM DESTINO d
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY d.id_destino, p.id_producto, pe.id_periodo;

INSERT INTO RESULTADOS_OPTIMIZACION 
(nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, num_viajes)
SELECT 
    o.nombre_origen,
    d.nombre_destino,
    c.tipo_camion,
    p.nombre_producto,
    pe.nombre_periodo,
    0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;

INSERT INTO RESULTADOS_X 
(nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, cantidad_tn)
SELECT 
    o.nombre_origen,
    d.nombre_destino,
    c.tipo_camion,
    p.nombre_producto,
    pe.nombre_periodo,
    0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo;

INSERT INTO RESULTADOS_RANGO
(nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, nombre_rango, cantidad_tn)
SELECT 
    o.nombre_origen,
    d.nombre_destino,
    c.tipo_camion,
    p.nombre_producto,
    pe.nombre_periodo,
    r.nombre_rango,
    0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
CROSS JOIN RANGO_COSTO r
ORDER BY o.id_origen, d.id_destino, c.id_camion, p.id_producto, pe.id_periodo, r.id_rango;
GO

-- ============================================================
-- VISTAS REQUERIDAS POR LINGO
-- ============================================================

CREATE VIEW VW_ORIGEN_ORDENADO AS
SELECT TOP (100) PERCENT
    nombre_origen
FROM ORIGEN
WHERE estado = 1
ORDER BY id_origen;
GO

CREATE VIEW VW_DESTINO_ORDENADO AS
SELECT TOP (100) PERCENT
    nombre_destino
FROM DESTINO
WHERE estado = 1
ORDER BY id_destino;
GO

CREATE VIEW VW_PRODUCTO_ORDENADO AS
SELECT TOP (100) PERCENT
    id_producto,
    nombre_producto,
    lote_minimo
FROM PRODUCTO
WHERE estado = 1
ORDER BY id_producto;
GO

CREATE VIEW VW_PERIODO_ORDENADO AS
SELECT TOP (100) PERCENT
    nombre_periodo
FROM PERIODO
WHERE estado = 1
ORDER BY id_periodo;
GO

CREATE VIEW VW_CAMION_ORDENADO AS
SELECT TOP (100) PERCENT
    id_camion,
    tipo_camion,
    capacidad_efectiva,
    costo_fijo
FROM CAMION
WHERE estado = 1
ORDER BY id_camion;
GO

CREATE VIEW VW_MATRIZ_COMPATIBILIDAD AS
SELECT TOP (100) PERCENT
    c.id_camion,
    p.id_producto,
    CASE 
        WHEN v.id_valida IS NOT NULL THEN 1 
        ELSE 0 
    END AS es_valido
FROM CAMION c
CROSS JOIN PRODUCTO p
LEFT JOIN VALIDA_CAMION_PRODUCTO v
    ON c.id_camion = v.id_camion
   AND p.id_producto = v.id_producto
   AND v.estado = 1
WHERE c.estado = 1
  AND p.estado = 1
ORDER BY c.id_camion, p.id_producto;
GO

CREATE VIEW VW_DISPONIBILIDAD_ORDENADO AS
SELECT TOP (100) PERCENT
    dc.id_camion,
    dc.id_periodo,
    dc.cantidad_viajes
FROM DISPONIBILIDAD_CAMION dc
WHERE dc.estado = 1
ORDER BY dc.id_camion, dc.id_periodo;
GO

CREATE VIEW VW_OFERTA_ORDENADO AS
SELECT TOP (100) PERCENT
    id_origen,
    id_producto,
    id_periodo,
    cantidad_tn
FROM OFERTA
ORDER BY id_origen, id_producto, id_periodo;
GO

CREATE VIEW VW_DEMANDA_ORDENADO AS
SELECT TOP (100) PERCENT
    id_destino,
    id_producto,
    id_periodo,
    cantidad_tn
FROM DEMANDA
ORDER BY id_destino, id_producto, id_periodo;
GO

CREATE VIEW VW_INVENTARIO_MIN_ORDENADO AS
SELECT TOP (100) PERCENT
    id_origen,
    id_producto,
    id_periodo,
    cantidad_minima
FROM INVENTARIO_MINIMO
WHERE estado = 1
ORDER BY id_origen, id_producto, id_periodo;
GO

CREATE VIEW VW_RANGO_ORDENADO AS
SELECT TOP (100) PERCENT
    id_rango,
    nombre_rango,
    limite_inferior,
    limite_superior
FROM RANGO_COSTO
WHERE estado = 1
ORDER BY id_rango;
GO

CREATE VIEW VW_COSTO_RANGO_ORDENADO AS
SELECT TOP (100) PERCENT
    id_origen,
    id_destino,
    id_producto,
    id_rango,
    costo_unitario
FROM COSTO_RANGO
WHERE estado = 1
ORDER BY id_origen, id_destino, id_producto, id_rango;
GO


TRUNCATE TABLE RESULTADOS_RANGO;
GO

INSERT INTO RESULTADOS_RANGO
(nombre_origen, nombre_destino, tipo_camion, nombre_producto, semana, nombre_rango, cantidad_tn)
SELECT 
    o.nombre_origen,
    d.nombre_destino,
    c.tipo_camion,
    p.nombre_producto,
    pe.nombre_periodo,
    r.nombre_rango,
    0.0
FROM ORIGEN o
CROSS JOIN DESTINO d
CROSS JOIN CAMION c
CROSS JOIN PRODUCTO p
CROSS JOIN PERIODO pe
CROSS JOIN RANGO_COSTO r
ORDER BY 
    o.id_origen,
    d.id_destino,
    c.id_camion,
    p.id_producto,
    pe.id_periodo,
    r.id_rango;
GO
