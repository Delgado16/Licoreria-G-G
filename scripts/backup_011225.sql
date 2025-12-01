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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (12,'Alimento preparado '),(1,'BEBIDAS'),(5,'CARNES'),(8,'CUIDADO PERSONAL'),(9,'ELECTRONICA'),(6,'FRUTAS Y VERDURAS'),(3,'LACTEOS'),(4,'LIMPIEZA'),(11,'OTROS'),(10,'PAPELERIA'),(2,'SNACKS');
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
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_facturacion`
--

LOCK TABLES `detalle_facturacion` WRITE;
/*!40000 ALTER TABLE `detalle_facturacion` DISABLE KEYS */;
INSERT INTO `detalle_facturacion` VALUES (1,1,1,1.00,75.00,75.00),(2,2,1,1.00,75.00,75.00),(3,3,1,1.00,75.00,75.00),(4,4,1,2.00,75.00,150.00),(5,5,1,2.00,75.00,150.00),(6,6,1,2.00,75.00,150.00),(7,7,1,2.00,75.00,150.00),(8,8,1,1.00,75.00,75.00),(9,9,1,1.00,75.00,75.00),(10,10,2,5.00,10.00,50.00),(11,11,1,9.00,75.00,675.00),(12,12,1,3.00,75.00,225.00),(13,12,2,3.00,10.00,30.00),(14,13,1,30.00,75.00,2250.00),(15,13,3,50.00,30.00,1500.00),(16,13,2,48.00,10.00,480.00),(17,14,2,4.00,10.00,40.00),(18,15,1,1.00,75.00,75.00),(19,16,1,1.00,75.00,75.00),(20,16,7,1.00,25.00,25.00),(21,17,9,6.00,65.00,390.00),(22,18,2,1.00,10.00,10.00),(23,19,7,1.00,25.00,25.00),(24,20,1,4.00,75.00,300.00),(25,21,1,1.00,75.00,75.00),(26,27,1,1.00,75.00,75.00),(27,28,11,7.00,60.00,420.00),(28,29,11,3.00,60.00,180.00),(29,30,9,1.00,65.00,65.00),(30,31,2,5.00,10.00,50.00),(31,32,9,7.00,65.00,455.00),(32,33,11,1.00,60.00,60.00),(33,33,5,1.00,10.00,10.00),(34,34,2,4.00,10.00,40.00),(35,35,10,1.00,2.00,2.00),(36,36,9,3.00,65.00,195.00),(37,37,5,1.00,10.00,10.00),(38,37,12,1.00,180.00,180.00),(39,38,8,15.00,43.00,645.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_movimiento_inventario`
--

LOCK TABLES `detalle_movimiento_inventario` WRITE;
/*!40000 ALTER TABLE `detalle_movimiento_inventario` DISABLE KEYS */;
INSERT INTO `detalle_movimiento_inventario` VALUES (1,1,1,144,500.00,72000.00),(2,2,2,24,8.00,192.00),(3,3,1,2,0.00,0.00),(4,4,1,2,0.00,0.00),(5,5,1,2,0.00,0.00),(6,6,1,1,0.00,0.00),(7,7,1,1,0.00,0.00),(8,8,2,5,0.00,0.00),(9,9,1,9,0.00,0.00),(10,10,1,3,0.00,0.00),(11,10,2,3,0.00,0.00),(12,11,3,50,10.00,500.00),(13,12,2,20,4.00,80.00),(14,13,1,1,60.00,60.00),(15,13,2,12,4.00,48.00),(16,14,1,30,0.00,0.00),(17,14,3,50,0.00,0.00),(18,14,2,48,0.00,0.00),(19,15,2,50,4.00,200.00),(20,16,2,5,0.00,0.00),(21,16,2,10,0.00,0.00),(22,17,2,4,0.00,0.00),(23,18,1,1,0.00,0.00),(24,19,5,50,12.00,600.00),(25,20,1,1,0.00,0.00),(26,20,7,1,0.00,0.00),(27,21,9,24,52.00,1248.00),(28,22,9,4,0.00,0.00),(29,23,9,6,0.00,0.00),(30,24,2,1,0.00,0.00),(31,25,7,1,0.00,0.00),(32,26,6,10,0.00,0.00),(33,27,1,4,0.00,0.00),(34,28,1,1,0.00,0.00),(35,29,1,1,0.00,0.00),(36,30,11,60,40.00,2400.00),(37,31,11,7,0.00,0.00),(38,32,11,3,60.00,180.00),(39,33,9,1,65.00,65.00),(40,34,2,5,10.00,50.00),(41,35,9,7,65.00,455.00),(42,36,11,1,60.00,60.00),(43,36,5,1,10.00,10.00),(44,37,2,4,10.00,40.00),(45,38,10,1,2.00,2.00),(46,39,5,5,0.00,0.00),(47,40,11,1,0.00,0.00),(48,41,9,3,65.00,195.00),(49,42,5,1,10.00,10.00),(50,42,12,1,180.00,180.00),(51,43,8,15,43.00,645.00),(52,44,2,10,4.00,40.00),(53,45,2,10,0.00,0.00),(58,48,2,10,4.00,40.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion`
--

LOCK TABLES `facturacion` WRITE;
/*!40000 ALTER TABLE `facturacion` DISABLE KEYS */;
INSERT INTO `facturacion` VALUES (1,'2025-11-21','09:02:16',75.00,100.00,25.00,1,'este maje es loco',2,1),(2,'2025-11-21','09:02:22',75.00,100.00,25.00,1,'este maje es loco',2,1),(3,'2025-11-21','09:02:26',75.00,100.00,25.00,1,'este maje es loco',2,1),(4,'2025-11-21','09:41:32',150.00,200.00,50.00,1,'ninguna\n',2,1),(5,'2025-11-21','11:05:58',150.00,200.00,50.00,1,'ninguno',2,1),(6,'2025-11-21','11:06:04',150.00,200.00,50.00,1,'ninguno',2,1),(7,'2025-11-21','11:06:08',150.00,200.00,50.00,1,'ninguno',2,1),(8,'2025-11-21','11:16:56',75.00,100.00,25.00,1,'ninguno',2,1),(9,'2025-11-21','11:29:15',75.00,100.00,25.00,1,'',2,1),(10,'2025-11-21','11:29:36',50.00,100.00,50.00,1,'nada',2,1),(11,'2025-11-26','17:08:31',675.00,680.00,5.00,1,'ninguna',2,1),(12,'2025-11-26','17:10:02',255.00,260.00,5.00,1,'',2,1),(13,'2025-11-29','15:05:24',4230.00,4300.00,70.00,1,'nada',2,1),(14,'2025-11-29','15:24:35',40.00,50.00,10.00,1,'',2,1),(15,'2025-11-29','15:25:11',75.00,0.00,0.00,4,'',2,1),(16,'2025-11-29','19:16:28',100.00,100.00,0.00,1,'ninguna',2,1),(17,'2025-11-29','21:23:37',390.00,400.00,10.00,1,'',2,1),(18,'2025-11-29','21:27:11',10.00,100.00,90.00,1,'',2,1),(19,'2025-11-29','21:27:37',25.00,25.00,0.00,1,'Crédito Nathaly',2,1),(20,'2025-11-29','23:02:12',300.00,300.00,0.00,1,'asdasdas',2,1),(21,'2025-11-29','23:04:32',75.00,100.00,25.00,1,'',2,1),(27,'2025-11-30','00:15:08',75.00,100.00,25.00,1,'ssd',2,1),(28,'2025-11-30','01:14:58',420.00,500.00,80.00,1,'ninguno',2,1),(29,'2025-11-30','01:36:59',180.00,200.00,20.00,1,'ninguna',2,1),(30,'2025-11-30','21:17:59',65.00,100.00,35.00,1,'',3,1),(31,'2025-11-30','21:22:54',50.00,60.00,10.00,1,'',3,1),(32,'2025-11-30','21:23:36',455.00,455.00,0.00,1,'',3,1),(33,'2025-11-30','21:29:24',70.00,100.00,30.00,1,'',4,1),(34,'2025-11-30','21:34:54',40.00,40.00,0.00,1,'Don Juan',4,1),(35,'2025-11-30','21:35:19',2.00,10.00,8.00,1,'',2,1),(36,'2025-11-30','21:52:20',195.00,195.00,0.00,1,'',2,1),(37,'2025-11-30','21:58:35',190.00,200.00,10.00,1,'',4,1),(38,'2025-11-30','22:33:38',645.00,1000.00,355.00,1,'',2,1);
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
INSERT INTO `inventario_bodega` VALUES (1,3,0.00),(1,13,10.00),(1,14,24.00),(1,6,26.00),(1,9,27.00),(1,8,30.00),(1,2,31.00),(1,7,32.00),(1,10,34.00),(1,12,34.00),(1,5,43.00),(1,1,87.00),(1,11,88.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (1,1,'ToñaLitro-211125','2025-11-21',1,'Recibiendo Julio',1),(2,1,'','2025-11-21',1,'banano me llamo yo',1),(3,2,NULL,'2025-11-21',NULL,'Venta - Factura #5',1),(4,2,NULL,'2025-11-21',NULL,'Venta - Factura #6',1),(5,2,NULL,'2025-11-21',NULL,'Venta - Factura #7',1),(6,2,NULL,'2025-11-21',NULL,'Venta - Factura #8',1),(7,2,NULL,'2025-11-21',NULL,'Venta - Factura #9',1),(8,2,NULL,'2025-11-21',NULL,'Venta - Factura #10',1),(9,2,NULL,'2025-11-26',NULL,'Venta - Factura #11',1),(10,2,NULL,'2025-11-26',NULL,'Venta - Factura #12',1),(11,1,'VD-1234','2025-11-26',2,'mayugados',1),(12,7,'Primer ingreso','2025-11-26',2,'mayugados',1),(13,1,'','2025-11-26',1,'',1),(14,2,NULL,'2025-11-29',NULL,'Venta - Factura #13',1),(15,3,'','2025-11-29',1,'',1),(16,12,NULL,'2025-11-29',NULL,'Mal estado ',1),(17,2,NULL,'2025-11-29',NULL,'Venta - Factura #14',1),(18,2,NULL,'2025-11-29',NULL,'Venta - Factura #15',1),(19,1,'01029922','2025-11-29',3,'',1),(20,2,NULL,'2025-11-29',NULL,'Venta - Factura #16',1),(21,1,'','2025-11-29',1,'',1),(22,10,NULL,'2025-11-29',NULL,'Consumo ',1),(23,2,NULL,'2025-11-29',NULL,'Venta - Factura #17',1),(24,2,NULL,'2025-11-29',NULL,'Venta - Factura #18',1),(25,2,NULL,'2025-11-29',NULL,'Venta - Factura #19',1),(26,2,NULL,'2025-11-29',NULL,'venta',1),(27,2,NULL,'2025-11-29',NULL,'Venta - Factura #20',1),(28,2,NULL,'2025-11-29',NULL,'Venta - Factura #21',1),(29,2,NULL,'2025-11-30',NULL,'Venta - Factura #27',1),(30,1,'CMP-000001','2025-11-30',1,'fsdfsdfsdf',1),(31,2,'VTA-000028','2025-11-30',NULL,'Venta - Factura #28',1),(32,2,'VTA-000029','2025-11-30',NULL,'Venta - Factura #29',1),(33,2,'VTA-000030','2025-11-30',NULL,'Venta - Factura #30',1),(34,2,'VTA-000031','2025-11-30',NULL,'Venta - Factura #31',1),(35,2,'VTA-000032','2025-11-30',NULL,'Venta - Factura #32',1),(36,2,'VTA-000033','2025-11-30',NULL,'Venta - Factura #33',1),(37,2,'VTA-000034','2025-11-30',NULL,'Venta - Factura #34',1),(38,2,'VTA-000035','2025-11-30',NULL,'Venta - Factura #35',1),(39,6,NULL,'2025-11-30',NULL,'Vencido ',1),(40,4,NULL,'2025-11-30',NULL,'Rebastecimiento',1),(41,2,'VTA-000036','2025-11-30',NULL,'Venta - Factura #36',1),(42,2,'VTA-000037','2025-11-30',NULL,'Venta - Factura #37',1),(43,2,'VTA-000038','2025-11-30',NULL,'Venta - Factura #38',1),(44,1,'056','2025-11-30',1,'',1),(45,6,NULL,'2025-11-30',NULL,'Mal estado',1),(48,1,'005','2025-11-30',2,'',1);
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
  KEY `idx_productos_usuario` (`Usuario_Creador`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`Unidad_Medida`) REFERENCES `unidades_medida` (`ID_Unidad`),
  CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`Categoria_ID`) REFERENCES `categorias` (`ID_Categoria`),
  CONSTRAINT `productos_ibfk_3` FOREIGN KEY (`Usuario_Creador`) REFERENCES `usuarios` (`ID_Usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Cerveza Toña 1 litro',4,1,60.00,75.00,1,'2025-10-21',2,24.00),(2,'Banano',1,0,4.00,10.00,6,'2025-10-21',2,10.00),(3,'Manzana',1,0,12.50,30.00,6,'2025-11-09',2,25.00),(4,'Maní ',1,0,0.00,20.00,2,'2025-11-26',2,1.00),(5,'Ranchita',1,1,7.00,10.00,2,'2025-11-29',2,10.00),(6,'TOÑA 12 ONZ',9,0,30.00,50.00,1,'2025-11-29',2,24.00),(7,'JOYITA 245MML',6,1,15.00,25.00,1,'2025-11-29',2,10.00),(8,'JOYITA 360MML',6,1,30.00,43.00,1,'2025-11-29',2,10.00),(9,'Cerveza sol',1,1,52.00,65.00,1,'2025-11-29',2,5.00),(10,'CURITAS',1,1,1.00,2.00,8,'2025-11-29',2,10.00),(11,'Maldito Catrin',1,1,40.00,60.00,1,'2025-11-30',2,25.00),(12,'RON PLATA GREEN APPLE 1000ML',1,1,120.00,180.00,1,'2025-11-30',2,20.00),(13,'Banano ',1,0,1.50,5.00,6,'2025-11-30',2,5.00),(14,'Seltzer 250ml',1,1,40.00,60.00,1,'2025-11-30',2,15.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'Cerveceria Nacional','89562374','Ca. Norte 1/2 buscando al aeropuerto','E78522CS5544'),(2,'Verduras','89562314','Roberto Huembe','230-963582-1005R'),(3,'Victoria ','57739641','','0012290929381a'),(5,'Cln','','',''),(7,'Productos Diana','78963251','x','R526582555SD'),(8,'Coca Cola','','','');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` VALUES (1,'UNIDAD','UND'),(2,'KILOGRAMO','KG'),(3,'GRAMO','GR'),(4,'LITRO','LT'),(6,'MILILITROS','MML'),(7,'PAQUETE','PQT'),(8,'CAJILLA','CJ'),(9,'ONZA','ONZ');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (2,'admin','scrypt:32768:8:1$FO95dAzWib7bal7w$7fe1092d8fbbcafdbfc5636644194a439ee247e6307a24f009e361efecae55c51512761dd0a8330628737ccb6175d1b952e2ad88e1946e37c026fd411fc666f8',1,1,'2025-10-21'),(3,'Julio@licoreria.com','scrypt:32768:8:1$0kOHa7vNUKlZzWbi$ee14ba80552af4154c02a3e10d39a220ef07cdf9d5254389959d31a6863c0813b4fd1da59d79b119d2ada84a1631f308b54b48dc9f3fc7e1d3685ae906ab1da7',2,1,'2025-11-30'),(4,'Valeska@licoreria.com','scrypt:32768:8:1$0cKer7DxfWDND4Ao$4ae8189294cebaed67beb13090014ebbac2beb6958439c259fa572a5fbe13c36ea5e075116d274d851f0af82cfe5d7ac97b187bac75f91d1be4c8d7d2897e04c',2,1,'2025-11-30'),(6,'Fared@licoreria.com','scrypt:32768:8:1$EHTJSJrpZ8kSIcuJ$fc4df7ad994ee5eea150c70651f1faaa691611c08655330d1ff297ff63cd4530a0a99546de82737e8f67804ce9c949d8035bd6c246dcf89c1a2a236fe8640dba',1,1,'2025-12-01');
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

-- Dump completed on 2025-12-01  0:58:34
