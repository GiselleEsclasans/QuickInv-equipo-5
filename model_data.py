# model_data.py
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

    # ================================
    #       Métodos Facturas
    # ================================
    def obtener_facturas_por_fecha(self):
        fechas = self.coleccion_facturas.distinct("fecha")
        return sorted(fechas, reverse=True) 

    def obtener_facturas_por_dia(self, fecha):
        return list(self.coleccion_facturas.find({"fecha": fecha}))

    def obtener_detalle_factura(self, numero_factura):
        return self.coleccion_facturas.find_one({"numero_factura": numero_factura})

    def cargar_datos(self, filepath: str):
        if not filepath:
            raise ValueError("La ruta del archivo es nula o vacía.")
        if filepath.endswith(".csv"):
            return pd.read_csv(filepath)
        elif filepath.endswith((".xlsx", ".xls")):
            return pd.read_excel(filepath)
        else:
            raise ValueError("El archivo debe ser un CSV o un Excel.")

    def calcular_estadisticas(self, df: pd.DataFrame) -> dict:
        return {
            "filas": df.shape[0],
            "columnas": df.shape[1],
            "columnas_nombres": list(df.columns),
        }

    # ================================
    #       Métodos Inventario
    # ================================
    def obtener_producto(self, categoria, id_producto):
        categoria = categoria.strip().lower()
        id_producto = id_producto.strip().upper()

        producto = self.coleccion_inventario.find_one({
            "id_producto": id_producto,
            "categoria": {"$regex": f"^{categoria}$", "$options": "i"}
        })
        if not producto:
            print(f"[ERROR] Producto con ID '{id_producto}' y Categoría '{categoria}' NO encontrado.")
        return producto

    def descontar_stock(self, id_producto, categoria, cantidad, fecha_factura):
        producto = self.obtener_producto(categoria, id_producto)
        if producto:
            stock_disponible = producto["cantidad_disponible"]
            if cantidad > stock_disponible:
                print(f"[ERROR] Stock insuficiente para '{producto['nombre_producto']}' (ID: {id_producto}).")
                return False
            nueva_cantidad = stock_disponible - cantidad
            fecha_actualizacion = (
                fecha_factura.strftime("%Y-%m-%d") 
                if isinstance(fecha_factura, datetime) 
                else str(fecha_factura)
            )
            movimiento = {
                "fecha": fecha_actualizacion,
                "tipo_movimiento": "venta",
                "cantidad": cantidad
            }
            self.coleccion_inventario.update_one(
                {"_id": producto["_id"]},
                {
                    "$set": {
                        "cantidad_disponible": nueva_cantidad, 
                        "ultima_actualizacion": fecha_actualizacion
                    },
                    "$push": {"historico_movimientos": movimiento}
                }
            )
            print(f"[DEBUG] Stock actualizado: {producto['nombre_producto']} - Nuevo stock: {nueva_cantidad}")
            return True
        else:
            print(f"[ERROR] No se pudo descontar stock: Producto {id_producto} no encontrado.")
            return False

    def actualizar_stock(self, producto, cantidad, fecha):
        nueva_cantidad = producto["cantidad_disponible"] - cantidad
        self.coleccion_inventario.update_one(
            {"_id": producto["_id"]},
            {"$set": {"cantidad_disponible": nueva_cantidad, "ultima_actualizacion": fecha}}
        )

    def insertar_facturas(self, facturas):
        self.coleccion_facturas.insert_many(facturas)

    # ================================
    #   NUEVAS FUNCIONES INVENTARIO
    # ================================
    def get_categorias(self):
        """Retorna la lista de categorías en inventario."""
        cats = self.coleccion_inventario.distinct("categoria")
        cats = sorted(cats)
        print("[DEBUG] Categorías encontradas en inventario:", cats)
        return cats

    def get_inventario_de_categoria(self, categoria):
        """Retorna la lista de productos de la categoría dada."""
        return list(self.coleccion_inventario.find({"categoria": categoria}))

    def actualizar_inventario_cantidad(self, id_producto, nueva_cantidad):
        """
        Ajusta la cantidad_disponible de 'id_producto' a 'nueva_cantidad'
        y registra un movimiento "ajuste_manual".
        """
        producto = self.coleccion_inventario.find_one({"id_producto": id_producto})
        if not producto:
            print(f"[ERROR] No se encontró producto con ID {id_producto} para actualizar.")
            return

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        movimiento = {
            "fecha": fecha_actual,
            "tipo_movimiento": "ajuste_manual",
            "cantidad": (nueva_cantidad - producto["cantidad_disponible"])
        }

        self.coleccion_inventario.update_one(
            {"_id": producto["_id"]},
            {
                "$set": {
                    "cantidad_disponible": nueva_cantidad,
                    "ultima_actualizacion": fecha_actual
                },
                "$push": {"historico_movimientos": movimiento}
            }
        )
        print(f"[DEBUG] Inventario '{producto['nombre_producto']}' actualizado a {nueva_cantidad}.")

 # -------------------------------
    # Nuevas funciones para análisis
    # -------------------------------
    def ventas_por_hora(self, fecha):
        pipeline = [
            {"$match": {"fecha": fecha}},
            {"$unwind": "$productos"},
            {"$project": {
                "hour": {"$substrCP": ["$hora", 0, 2]},
                "cantidad": "$productos.cantidad",
                "nombre_producto": "$productos.nombre_producto"
            }},
            {"$group": {
                "_id": {"hour": "$hour", "nombre_producto": "$nombre_producto"},
                "total": {"$sum": "$cantidad"}
            }},
            {"$sort": {"_id.hour": 1, "total": -1}},
            {"$group": {
                "_id": "$_id.hour",
                "top_product": {"$first": "$_id.nombre_producto"},
                "total": {"$first": "$total"}
            }},
            {"$sort": {"_id": 1}}
        ]
        results = self.coleccion_facturas.aggregate(pipeline)
        data = []
        for r in results:
            hour_str = r["_id"]
            top_product = r["top_product"]
            total = r["total"]
            data.append((hour_str, top_product, total))
        return data

    def ventas_productos_por_dia(self, fecha):
        pipeline = [
            {"$match": {"fecha": fecha}},
            {"$unwind": "$productos"},
            {"$group": {
                "_id": "$productos.nombre_producto",
                "total": {"$sum": "$productos.cantidad"}
            }},
            {"$sort": {"total": -1}}
        ]
        results = self.coleccion_facturas.aggregate(pipeline)
        data = []
        for r in results:
            product = r["_id"]
            total = r["total"]
            data.append((product, total))
        return data

    def ventas_por_dia(self):
        pipeline = [
            {"$unwind": "$productos"},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha"}},
                "total": {"$sum": "$productos.subtotal"}
            }},
            {"$sort": {"_id": 1}}
        ]
        results = self.coleccion_facturas.aggregate(pipeline)
        data = []
        for r in results:
            dia_str = r["_id"]
            total = r["total"]
            data.append((dia_str, total))
        return data

    def desempeno_financiero(self):
        pipeline = [
            {"$unwind": "$productos"},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m", "date": "$fecha"}},
                "total": {"$sum": "$productos.subtotal"}
            }},
            {"$sort": {"_id": 1}}
        ]
        results = self.coleccion_facturas.aggregate(pipeline)
        data = []
        for r in results:
            mes_str = r["_id"]
            total = r["total"]
            data.append((mes_str, total))
        return data

    def desempeno_financiero_diario(self):
        pipeline = [
            {"$unwind": "$productos"},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha"}},
                "total": {"$sum": "$productos.subtotal"}
            }},
            {"$sort": {"_id": 1}}
        ]
        results = self.coleccion_facturas.aggregate(pipeline)
        data = []
        for r in results:
            day_str = r["_id"]
            total = r["total"]
            data.append((day_str, total))
        return data

    def horarios_criticos(self):
        pipeline = [
            {"$unwind": "$productos"},
            {"$project": {
                "dow": {"$dayOfWeek": "$fecha"},
                "hour": {"$substrCP": ["$hora", 0, 2]},
                "subtotal": "$productos.subtotal"
            }},
            {"$group": {
                "_id": {"dow": "$dow", "hour": "$hour"},
                "total": {"$sum": "$subtotal"}
            }},
            {"$sort": {"_id.dow": 1, "_id.hour": 1}}
        ]
        results = self.coleccion_facturas.aggregate(pipeline)
        dow_map = {1:"Dom", 2:"Lun", 3:"Mar", 4:"Mié", 5:"Jue", 6:"Vie", 7:"Sáb"}
        data_map = {}
        all_hours = set()
        all_days = set()
        for r in results:
            dow_num = r["_id"]["dow"]
            hour_str = r["_id"]["hour"]
            total = r["total"]
            day_str = dow_map.get(dow_num, f"D{dow_num}")
            if day_str not in data_map:
                data_map[day_str] = {}
            data_map[day_str][hour_str] = total
            all_days.add(day_str)
            all_hours.add(hour_str)
        sorted_days = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        sorted_days = [d for d in sorted_days if d in all_days]
        sorted_hours = sorted(list(all_hours), key=lambda x: int(x))
        z = []
        for d in sorted_days:
            row = []
            for h in sorted_hours:
                val = data_map.get(d, {}).get(h, 0)
                row.append(val)
            z.append(row)
        return (sorted_hours, sorted_days, z)