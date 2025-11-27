CREATE DATABASE  IF NOT EXISTS `proyecto` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `proyecto`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: proyecto
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bodegas`
--

DROP TABLE IF EXISTS `bodegas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bodegas` (
  `ID_Bodega` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(255) NOT NULL,
  `Ubicacion` text,
  PRIMARY KEY (`ID_Bodega`),
  KEY `idx_bodegas_nombre` (`Nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bodegas`
--

LOCK TABLES `bodegas` WRITE;
/*!40000 ALTER TABLE `bodegas` DISABLE KEYS */;
INSERT INTO `bodegas` VALUES (1,'BODEGA PRINCIPAL','LOCAL CENTRAL');
/*!40000 ALTER TABLE `bodegas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_movimientos`
--

DROP TABLE IF EXISTS `catalogo_movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_movimientos` (
  `ID_TipoMovimiento` int NOT NULL AUTO_INCREMENT,
  `Descripcion` varchar(255) DEFAULT NULL,
  `Adicion` varchar(50) DEFAULT NULL,
  `Letra` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ID_TipoMovimiento`),
  KEY `idx_movimientos_descripcion` (`Descripcion`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_movimientos`
--

LOCK TABLES `catalogo_movimientos` WRITE;
/*!40000 ALTER TABLE `catalogo_movimientos` DISABLE KEYS */;
INSERT INTO `catalogo_movimientos` VALUES (1,'COMPRA','ENTRADA','E'),(2,'VENTA','SALIDA','S'),(3,'AJUSTE INVENTARIO','ENTRADA','E'),(4,'TRASLADO','SALIDA','S'),(5,'DEVOLUCION CLIENTE','ENTRADA','E'),(6,'DEVOLUCION PROVEEDOR','SALIDA','S'),(7,'COMPRA','ENTRADA','E'),(8,'VENTA','SALIDA','S'),(9,'AJUSTE INVENTARIO','ENTRADA','E'),(10,'TRASLADO','SALIDA','S'),(11,'DEVOLUCION CLIENTE','ENTRADA','E'),(12,'DEVOLUCION PROVEEDOR','SALIDA','S');
/*!40000 ALTER TABLE `catalogo_movimientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `ID_Categoria` int NOT NULL AUTO_INCREMENT,
  `Descripcion` varchar(255) NOT NULL,
  PRIMARY KEY (`ID_Categoria`),
  KEY `idx_categorias_descripcion` (`Descripcion`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'BEBIDAS'),(5,'CARNES'),(8,'CUIDADO PERSONAL'),(9,'ELECTRONICA'),(6,'FRUTAS Y VERDURAS'),(3,'LACTEOS'),(4,'LIMPIEZA'),(11,'OTROS'),(7,'PANADERIA'),(10,'PAPELERIA'),(2,'SNACKS');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_facturacion`
--

DROP TABLE IF EXISTS `detalle_facturacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_facturacion` (
  `ID_Detalle` int NOT NULL AUTO_INCREMENT,
  `ID_Factura` int DEFAULT NULL,
  `ID_Producto` int DEFAULT NULL,
  `Cantidad` decimal(15,2) DEFAULT NULL,
  `Precio_Venta` decimal(15,2) DEFAULT NULL,
  `Subtotal` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`ID_Detalle`),
  KEY `idx_detalle_factura` (`ID_Factura`),
  KEY `idx_detalle_producto` (`ID_Producto`),
  KEY `idx_detalle_factura_producto` (`ID_Factura`,`ID_Producto`),
  CONSTRAINT `detalle_facturacion_ibfk_1` FOREIGN KEY (`ID_Factura`) REFERENCES `facturacion` (`ID_Factura`),
  CONSTRAINT `detalle_facturacion_ibfk_2` FOREIGN KEY (`ID_Producto`) REFERENCES `productos` (`ID_Producto`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_facturacion`
--

LOCK TABLES `detalle_facturacion` WRITE;
/*!40000 ALTER TABLE `detalle_facturacion` DISABLE KEYS */;
INSERT INTO `detalle_facturacion` VALUES (1,1,1,1.00,75.00,75.00),(2,2,1,1.00,75.00,75.00),(3,3,1,1.00,75.00,75.00),(4,4,1,2.00,75.00,150.00),(5,5,1,2.00,75.00,150.00),(6,6,1,2.00,75.00,150.00),(7,7,1,2.00,75.00,150.00),(8,8,1,1.00,75.00,75.00),(9,9,1,1.00,75.00,75.00),(10,10,2,5.00,10.00,50.00),(11,11,1,9.00,75.00,675.00),(12,12,1,3.00,75.00,225.00),(13,12,2,3.00,10.00,30.00);
/*!40000 ALTER TABLE `detalle_facturacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_movimiento_inventario`
--

DROP TABLE IF EXISTS `detalle_movimiento_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_movimiento_inventario` (
  `ID_Detalle` int NOT NULL AUTO_INCREMENT,
  `ID_Movimiento` int DEFAULT NULL,
  `ID_Producto` int DEFAULT NULL,
  `Cantidad` int DEFAULT NULL,
  `Costo` decimal(15,2) DEFAULT NULL,
  `Costo_Total` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`ID_Detalle`),
  KEY `idx_detalle_movimiento` (`ID_Movimiento`),
  KEY `idx_detalle_movimiento_producto` (`ID_Producto`),
  KEY `idx_detalle_movimiento_compuesto` (`ID_Movimiento`,`ID_Producto`),
  CONSTRAINT `detalle_movimiento_inventario_ibfk_1` FOREIGN KEY (`ID_Movimiento`) REFERENCES `movimientos_inventario` (`ID_Movimiento`),
  CONSTRAINT `detalle_movimiento_inventario_ibfk_2` FOREIGN KEY (`ID_Producto`) REFERENCES `productos` (`ID_Producto`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_movimiento_inventario`
--

LOCK TABLES `detalle_movimiento_inventario` WRITE;
/*!40000 ALTER TABLE `detalle_movimiento_inventario` DISABLE KEYS */;
INSERT INTO `detalle_movimiento_inventario` VALUES (1,1,1,144,500.00,72000.00),(2,2,2,24,8.00,192.00),(3,3,1,2,0.00,0.00),(4,4,1,2,0.00,0.00),(5,5,1,2,0.00,0.00),(6,6,1,1,0.00,0.00),(7,7,1,1,0.00,0.00),(8,8,2,5,0.00,0.00),(9,9,1,9,0.00,0.00),(10,10,1,3,0.00,0.00),(11,10,2,3,0.00,0.00);
/*!40000 ALTER TABLE `detalle_movimiento_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion`
--

DROP TABLE IF EXISTS `facturacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion` (
  `ID_Factura` int NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL DEFAULT (curdate()),
  `Hora` time NOT NULL DEFAULT (curtime()),
  `Total` decimal(15,2) NOT NULL,
  `Efectivo` decimal(15,2) DEFAULT NULL,
  `Cambio` decimal(15,2) DEFAULT NULL,
  `ID_MetodoPago` int DEFAULT NULL,
  `Observacion` text,
  `ID_Usuario` int DEFAULT NULL,
  `Estado` tinyint DEFAULT '1',
  PRIMARY KEY (`ID_Factura`),
  KEY `idx_facturacion_fecha` (`Fecha`),
  KEY `idx_facturacion_usuario` (`ID_Usuario`),
  KEY `idx_facturacion_metodo_pago` (`ID_MetodoPago`),
  KEY `idx_facturacion_estado` (`Estado`),
  KEY `idx_facturacion_fecha_hora` (`Fecha`,`Hora`),
  CONSTRAINT `facturacion_ibfk_1` FOREIGN KEY (`ID_MetodoPago`) REFERENCES `metodos_pago` (`ID_MetodoPago`),
  CONSTRAINT `facturacion_ibfk_2` FOREIGN KEY (`ID_Usuario`) REFERENCES `usuarios` (`ID_Usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion`
--

LOCK TABLES `facturacion` WRITE;
/*!40000 ALTER TABLE `facturacion` DISABLE KEYS */;
INSERT INTO `facturacion` VALUES (1,'2025-11-21','09:02:16',75.00,100.00,25.00,1,'este maje es loco',2,1),(2,'2025-11-21','09:02:22',75.00,100.00,25.00,1,'este maje es loco',2,1),(3,'2025-11-21','09:02:26',75.00,100.00,25.00,1,'este maje es loco',2,1),(4,'2025-11-21','09:41:32',150.00,200.00,50.00,1,'ninguna\n',2,1),(5,'2025-11-21','11:05:58',150.00,200.00,50.00,1,'ninguno',2,1),(6,'2025-11-21','11:06:04',150.00,200.00,50.00,1,'ninguno',2,1),(7,'2025-11-21','11:06:08',150.00,200.00,50.00,1,'ninguno',2,1),(8,'2025-11-21','11:16:56',75.00,100.00,25.00,1,'ninguno',2,1),(9,'2025-11-21','11:29:15',75.00,100.00,25.00,1,'',2,1),(10,'2025-11-21','11:29:36',50.00,100.00,50.00,1,'nada',2,1),(11,'2025-11-26','17:08:31',675.00,680.00,5.00,1,'ninguna',2,1),(12,'2025-11-26','17:10:02',255.00,260.00,5.00,1,'',2,1);
/*!40000 ALTER TABLE `facturacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_bodega`
--

DROP TABLE IF EXISTS `inventario_bodega`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario_bodega` (
  `ID_Bodega` int NOT NULL,
  `ID_Producto` int NOT NULL,
  `Existencias` decimal(15,2) DEFAULT '0.00',
  PRIMARY KEY (`ID_Bodega`,`ID_Producto`),
  KEY `idx_inventario_bodega` (`ID_Bodega`),
  KEY `idx_inventario_producto` (`ID_Producto`),
  KEY `idx_inventario_existencias` (`Existencias`),
  CONSTRAINT `inventario_bodega_ibfk_1` FOREIGN KEY (`ID_Bodega`) REFERENCES `bodegas` (`ID_Bodega`),
  CONSTRAINT `inventario_bodega_ibfk_2` FOREIGN KEY (`ID_Producto`) REFERENCES `productos` (`ID_Producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_bodega`
--

LOCK TABLES `inventario_bodega` WRITE;
/*!40000 ALTER TABLE `inventario_bodega` DISABLE KEYS */;
INSERT INTO `inventario_bodega` VALUES (1,2,16.00),(1,1,124.00);
/*!40000 ALTER TABLE `inventario_bodega` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metodos_pago`
--

DROP TABLE IF EXISTS `metodos_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metodos_pago` (
  `ID_MetodoPago` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(255) NOT NULL,
  PRIMARY KEY (`ID_MetodoPago`),
  KEY `idx_metodos_nombre` (`Nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metodos_pago`
--

LOCK TABLES `metodos_pago` WRITE;
/*!40000 ALTER TABLE `metodos_pago` DISABLE KEYS */;
INSERT INTO `metodos_pago` VALUES (1,'EFECTIVO'),(3,'TARJETA CRÉDITO'),(2,'TARJETA DÉBITO'),(4,'TRANSFERENCIA');
/*!40000 ALTER TABLE `metodos_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_inventario` (
  `ID_Movimiento` int NOT NULL AUTO_INCREMENT,
  `ID_TipoMovimiento` int DEFAULT NULL,
  `N_Factura` varchar(255) DEFAULT NULL,
  `Fecha` date DEFAULT (curdate()),
  `ID_Proveedor` int DEFAULT NULL,
  `Observacion` text,
  `ID_Bodega` int DEFAULT NULL,
  PRIMARY KEY (`ID_Movimiento`),
  KEY `idx_movimientos_tipo` (`ID_TipoMovimiento`),
  KEY `idx_movimientos_fecha` (`Fecha`),
  KEY `idx_movimientos_proveedor` (`ID_Proveedor`),
  KEY `idx_movimientos_bodega` (`ID_Bodega`),
  KEY `idx_movimientos_nfactura` (`N_Factura`),
  KEY `idx_movimientos_fecha_tipo` (`Fecha`,`ID_TipoMovimiento`),
  CONSTRAINT `movimientos_inventario_ibfk_1` FOREIGN KEY (`ID_TipoMovimiento`) REFERENCES `catalogo_movimientos` (`ID_TipoMovimiento`),
  CONSTRAINT `movimientos_inventario_ibfk_2` FOREIGN KEY (`ID_Proveedor`) REFERENCES `proveedores` (`ID_Proveedor`),
  CONSTRAINT `movimientos_inventario_ibfk_3` FOREIGN KEY (`ID_Bodega`) REFERENCES `bodegas` (`ID_Bodega`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (1,1,'ToñaLitro-211125','2025-11-21',1,'Recibiendo Julio',1),(2,1,'','2025-11-21',1,'banano me llamo yo',1),(3,2,NULL,'2025-11-21',NULL,'Venta - Factura #5',1),(4,2,NULL,'2025-11-21',NULL,'Venta - Factura #6',1),(5,2,NULL,'2025-11-21',NULL,'Venta - Factura #7',1),(6,2,NULL,'2025-11-21',NULL,'Venta - Factura #8',1),(7,2,NULL,'2025-11-21',NULL,'Venta - Factura #9',1),(8,2,NULL,'2025-11-21',NULL,'Venta - Factura #10',1),(9,2,NULL,'2025-11-26',NULL,'Venta - Factura #11',1),(10,2,NULL,'2025-11-26',NULL,'Venta - Factura #12',1);
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `ID_Producto` int NOT NULL AUTO_INCREMENT,
  `Descripcion` varchar(255) NOT NULL,
  `Unidad_Medida` int DEFAULT NULL,
  `Existencias` decimal(15,2) DEFAULT '0.00',
  `Estado` tinyint DEFAULT '1',
  `Costo_Promedio` decimal(15,2) DEFAULT NULL,
  `Precio_Venta` decimal(15,2) DEFAULT NULL,
  `Categoria_ID` int DEFAULT NULL,
  `Fecha_Creacion` date DEFAULT (curdate()),
  `Usuario_Creador` int DEFAULT NULL,
  `Stock_Minimo` decimal(15,2) DEFAULT '5.00',
  PRIMARY KEY (`ID_Producto`),
  KEY `idx_productos_descripcion` (`Descripcion`),
  KEY `idx_productos_unidad` (`Unidad_Medida`),
  KEY `idx_productos_categoria` (`Categoria_ID`),
  KEY `idx_productos_estado` (`Estado`),
  KEY `idx_productos_existencias` (`Existencias`),
  KEY `idx_productos_usuario` (`Usuario_Creador`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`Unidad_Medida`) REFERENCES `unidades_medida` (`ID_Unidad`),
  CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`Categoria_ID`) REFERENCES `categorias` (`ID_Categoria`),
  CONSTRAINT `productos_ibfk_3` FOREIGN KEY (`Usuario_Creador`) REFERENCES `usuarios` (`ID_Usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Cerveza Toña 1 litro',4,124.00,1,60.00,75.00,1,'2025-10-21',2,24.00),(2,'Banano',1,16.00,1,4.00,10.00,6,'2025-10-21',2,6.00),(3,'Manzana',1,0.00,1,15.00,30.00,6,'2025-11-09',2,25.00);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `ID_Proveedor` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(255) NOT NULL,
  `Telefono` varchar(50) DEFAULT NULL,
  `Direccion` text,
  `RUC_CEDULA` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID_Proveedor`),
  KEY `idx_proveedores_nombre` (`Nombre`),
  KEY `idx_proveedores_ruc` (`RUC_CEDULA`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'Cerveceria Nacional','89562374','Ca. Norte 1/2 buscando al aeropuerto','E78522CS5544'),(2,'Verduras','89562314','Roberto Huembe','230-963582-1005R');
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `ID_Rol` int NOT NULL AUTO_INCREMENT,
  `Nombre_Rol` varchar(255) NOT NULL,
  PRIMARY KEY (`ID_Rol`),
  KEY `idx_roles_nombre` (`Nombre_Rol`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador'),(2,'Vendedor');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidades_medida`
--

DROP TABLE IF EXISTS `unidades_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidades_medida` (
  `ID_Unidad` int NOT NULL AUTO_INCREMENT,
  `Descripcion` varchar(255) NOT NULL,
  `Abreviatura` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_Unidad`),
  KEY `idx_unidades_descripcion` (`Descripcion`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` VALUES (1,'UNIDAD','UND'),(2,'KILOGRAMO','KG'),(3,'GRAMO','GR'),(4,'LITRO','LT'),(5,'METRO','MT'),(6,'MILILITROS','MML'),(7,'PAQUETE','PQT'),(8,'CAJILLA','CJ');
/*!40000 ALTER TABLE `unidades_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `ID_Usuario` int NOT NULL AUTO_INCREMENT,
  `NombreUsuario` varchar(255) NOT NULL,
  `ContrasenaHash` varchar(255) NOT NULL,
  `Rol_ID` int DEFAULT NULL,
  `Estado` tinyint DEFAULT '1',
  `Fecha_Creacion` date DEFAULT (curdate()),
  PRIMARY KEY (`ID_Usuario`),
  UNIQUE KEY `NombreUsuario` (`NombreUsuario`),
  KEY `idx_usuarios_nombre` (`NombreUsuario`),
  KEY `idx_usuarios_rol` (`Rol_ID`),
  KEY `idx_usuarios_estado` (`Estado`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`Rol_ID`) REFERENCES `roles` (`ID_Rol`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (2,'admin','scrypt:32768:8:1$FO95dAzWib7bal7w$7fe1092d8fbbcafdbfc5636644194a439ee247e6307a24f009e361efecae55c51512761dd0a8330628737ccb6175d1b952e2ad88e1946e37c026fd411fc666f8',1,1,'2025-10-21');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'proyecto'
--

--
-- Dumping routines for database 'proyecto'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-26 18:24:19
