# Description: Clase que se encarga de la conexión con MongoDB Atlas y de realizar operaciones CRUD.
import pymongo
import pandas as pd

class DataModel:
    def __init__(self):
        """Conectar a MongoDB Atlas"""
        mongo_uri = "mongodb+srv://Analista:Analista1234-@cluster0.d90b1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = pymongo.MongoClient(mongo_uri)
        self.db_inventario = self.client["Inventario"]
        self.coleccion_inventario = self.db_inventario["inventario_col"] 

        self.db_facturas = self.client["Facturas"] 
        self.coleccion_facturas = self.db_facturas["facturas_col"]

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
        producto = self.coleccion_inventario.find_one({"id_producto": id_producto, "categoria": categoria})

        if not producto:
            print(f" Producto con ID '{id_producto}' y Categoría '{categoria}' NO encontrado en inventario.")

        return producto  # Retorna `None` si el producto no existe


    def descontar_stock(self, id_producto, categoria, cantidad):
        """Descuenta `cantidad` del stock de `id_producto` en `inventario_col`."""
        producto = self.obtener_producto(categoria, id_producto)  # Se usa la categoría real

        if producto:
            nueva_cantidad = max(producto["cantidad_disponible"] - cantidad, 0)  # Evita valores negativos
            self.coleccion_inventario.update_one(
                {"_id": producto["_id"]},
                {"$set": {"cantidad_disponible": nueva_cantidad}}
            )
            print(f"Stock actualizado: {producto['nombre_producto']} (ID: {id_producto}) - Nuevo stock: {nueva_cantidad}")
        else:
            print(f" No se pudo descontar stock: Producto {id_producto} no encontrado.")


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
