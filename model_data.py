# Description: Clase que se encarga de la conexión con MongoDB Atlas y de realizar operaciones CRUD.
import pymongo
import pandas as pd
from datetime import datetime

class DataModel:
    def __init__(self):
        """Conectar a MongoDB Atlas"""
        mongo_uri = "mongodb+srv://Analista:Analista1234-@cluster0.d90b1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = pymongo.MongoClient(mongo_uri)
        self.db_inventario = self.client["Inventario"]
        self.coleccion_inventario = self.db_inventario["inventario_col"] 

        self.db_facturas = self.client["Facturas"] 
        self.coleccion_facturas = self.db_facturas["facturas_col"]

    
    def obtener_facturas_por_fecha(self):
        """✅ Obtiene todas las fechas únicas en las que se han cargado facturas."""
        fechas = self.coleccion_facturas.distinct("fecha")
        return sorted(fechas, reverse=True)  # 🔹 Ordenadas por fecha descendente

    def obtener_facturas_por_dia(self, fecha):
        """✅ Obtiene todas las facturas de un día específico."""
        return list(self.coleccion_facturas.find({"fecha": fecha}))

    def obtener_detalle_factura(self, numero_factura):
        """✅ Obtiene el detalle completo de una factura por su número."""
        return self.coleccion_facturas.find_one({"numero_factura": numero_factura})


    def cargar_datos(self, filepath: str):
        """Carga datos desde un archivo CSV o Excel y los almacena en un DataFrame."""
        if not filepath:
            raise ValueError("La ruta del archivo es nula o vacía.")
        if filepath.endswith(".csv"):
            return pd.read_csv(filepath)
        elif filepath.endswith((".xlsx", ".xls")):
            return pd.read_excel(filepath)
        else:
            raise ValueError("El archivo debe ser un CSV o un Excel.")

    def calcular_estadisticas(self, df: pd.DataFrame) -> dict:
        """Calcula estadísticas básicas del DataFrame."""
        return {
            "filas": df.shape[0],
            "columnas": df.shape[1],
            "columnas_nombres": list(df.columns),
        }

    def obtener_producto(self, categoria, id_producto):
        """✅ Verifica si el producto existe en `inventario_col`."""
        categoria = categoria.strip().lower()
        id_producto = id_producto.strip().upper()

        producto = self.coleccion_inventario.find_one({
            "id_producto": id_producto,
            "categoria": {"$regex": f"^{categoria}$", "$options": "i"}  # 🔹 Ignorar mayúsculas y espacios
        })

        if not producto:
            print(f"[ERROR] Producto con ID '{id_producto}' y Categoría '{categoria}' NO encontrado en inventario.")

        return producto  # Retorna `None` si el producto no existe


    def descontar_stock(self, id_producto, categoria, cantidad, fecha_factura):
        """✅ Descuenta `cantidad` del stock de `id_producto` en `inventario_col`, si hay suficiente stock."""
        producto = self.obtener_producto(categoria, id_producto)

        if producto:
            stock_disponible = producto["cantidad_disponible"]

            if cantidad > stock_disponible:
                print(f"Cuidado: Stock insuficiente para el producto {producto['nombre_producto']} (ID: {id_producto}).")
                print(f"   Stock disponible: {stock_disponible}, cantidad requerida: {cantidad}. Faltan {cantidad - stock_disponible} unidades.")
                return False  # ❌ No se puede procesar la factura con este producto

            
            nueva_cantidad = stock_disponible - cantidad  # Reducimos el stock
            fecha_actualizacion = fecha_factura.strftime("%Y-%m-%d") if isinstance(fecha_factura, datetime) else str(fecha_factura)
            
             # 🔹 Agregar movimiento al historial de ventas
            movimiento = {
                "fecha": fecha_actualizacion,
                "tipo_movimiento": "venta",
                "cantidad": cantidad
            }

            
            self.coleccion_inventario.update_one(
                {"_id": producto["_id"]},
                {
                    "$set": {"cantidad_disponible": nueva_cantidad, "ultima_actualizacion": fecha_actualizacion},
                    "$push": {"historico_movimientos": movimiento}
                }
            )

            print(f"Stock actualizado: {producto['nombre_producto']} (ID: {id_producto}) - Nuevo stock: {nueva_cantidad}")
            return True  # ✅ Se procesó correctamente

        else:
            print(f"No se pudo descontar stock: Producto {id_producto} no encontrado.")
            return False  # ❌ No se encontró el producto


    def actualizar_stock(self, producto, cantidad, fecha):
        """Actualiza el stock del inventario."""
        nueva_cantidad = producto["cantidad_disponible"] - cantidad
        self.coleccion_inventario.update_one(
            {"_id": producto["_id"]},
            {"$set": {"cantidad_disponible": nueva_cantidad, "ultima_actualizacion": fecha}}
        )

    def insertar_facturas(self, facturas):
        """Inserta facturas en la base de datos `Facturas.facturas_col`."""
        self.coleccion_facturas.insert_many(facturas)

    def aumentar_stock(self, id_producto, cantidad):
        self.coleccion_inventario.update_one(
            {"id_producto": id_producto},
            {"$inc": {"cantidad_disponible": cantidad}, "$set": {"ultima_actualizacion": datetime.now().strftime("%Y-%m-%d")}}
        )
    
    def disminuir_stock(self, id_producto, cantidad):
        producto = self.coleccion_inventario.find_one({"id_producto": id_producto})
        if producto and cantidad <= producto["cantidad_disponible"]:
            self.coleccion_inventario.update_one(
                {"id_producto": id_producto},
                {"$inc": {"cantidad_disponible": -cantidad}, "$set": {"ultima_actualizacion": datetime.now().strftime("%Y-%m-%d")}}
            )
            return True
        return False
