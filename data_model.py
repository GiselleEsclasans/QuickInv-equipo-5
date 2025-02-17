# data_model.py
import pandas as pd

def cargar_datos(filepath: str):
    if not filepath:
        raise ValueError("La ruta del archivo es nula o vacía.")
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath)
    elif filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError("El archivo debe ser un CSV o un Excel.")

def calcular_estadisticas(df: pd.DataFrame) -> dict:
    return {
        "filas": df.shape[0],
        "columnas": df.shape[1],
        "columnas_nombres": list(df.columns),
    }

import pandas as pd
import pymongo
from datetime import datetime

def procesar_facturas(archivos, db):
    """
    Procesa archivos de facturas en formato .xlsx o .csv y actualiza el inventario en la base de datos MongoDB.
    
    Parámetros:
        archivos (list): Lista de rutas de archivos .xlsx o .csv con facturas.
        db (pymongo.database.Database): Conexión a la base de datos MongoDB.
    
    Retorna:
        None: Imprime mensajes de error o éxito según corresponda.
    """
    try:
        coleccion_inventario = db["Inventario"]["inventario_col"]
        coleccion_facturas = db["Facturas"]["facturas_col"]
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return
    
    for archivo in archivos:
        try:
            if archivo.endswith('.xlsx'):
                df = pd.read_excel(archivo)
            elif archivo.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                print(f"Error: Formato de archivo no soportado -> {archivo}")
                continue
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
            continue
        
        facturas_procesadas = {}
        
        for index, fila in df.iterrows():
            try:
                numero_factura = fila['Número Factura']
                categoria = fila['Categoría']
                id_producto = fila['ID Producto']
                cantidad = fila['Cantidad']
                fecha_factura = fila['Fecha']
                hora_factura = fila['Hora']
                id_cliente = fila['ID Cliente']
                nombre_cliente = fila['Nombre Cliente']
                precio_unitario = fila['Precio Unitario']
                subtotal = fila['Subtotal']
                
                if not isinstance(cantidad, int) or cantidad <= 0:
                    print(f"Error en archivo {archivo}, fila {index + 2}, factura {numero_factura}: La cantidad no es un número entero positivo.")
                    continue
                
                producto = coleccion_inventario.find_one({"categoria": categoria, "id_producto": id_producto})
                
                if not producto:
                    print(f"Error en archivo {archivo}, fila {index + 2}, factura {numero_factura}: Categoría '{categoria}' o producto '{id_producto}' no existen.")
                    continue
                
                if producto['id_producto'] != id_producto:
                    print(f"Error en archivo {archivo}, fila {index + 2}, factura {numero_factura}: ID del producto incorrecto.")
                    continue
                
                if producto['precio_unitario'] != precio_unitario:
                    print(f"Error en archivo {archivo}, fila {index + 2}, factura {numero_factura}: Precio unitario incorrecto para el producto '{id_producto}'.")
                    continue
                
                if producto['cantidad_disponible'] < cantidad:
                    print(f"Error en archivo {archivo}, fila {index + 2}, factura {numero_factura}: Stock insuficiente para el producto '{id_producto}'.")
                    continue
                
                nueva_cantidad = producto['cantidad_disponible'] - cantidad
                coleccion_inventario.update_one(
                    {"_id": producto['_id']},
                    {"$set": {"cantidad_disponible": nueva_cantidad, "ultima_actualizacion": fecha_factura}}
                )
                
                if numero_factura not in facturas_procesadas:
                    facturas_procesadas[numero_factura] = {
                        "numero_factura": numero_factura,
                        "fecha": fecha_factura,
                        "hora": hora_factura,
                        "cliente": {"id_cliente": id_cliente, "nombre": nombre_cliente},
                        "productos": [],
                        "total_factura": 0
                    }
                
                facturas_procesadas[numero_factura]["productos"].append({
                    "id_producto": id_producto,
                    "nombre_producto": fila['Nombre Producto'],
                    "categoria": categoria,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal
                })
                facturas_procesadas[numero_factura]["total_factura"] += subtotal
                
                print(f"Factura {numero_factura} en archivo {archivo} procesada correctamente. Stock actualizado.")
            except Exception as e:
                print(f"Error inesperado en archivo {archivo}, fila {index + 2}, factura {numero_factura}: {e}")
                continue
        
        if facturas_procesadas:
            try:
                coleccion_facturas.insert_many(facturas_procesadas.values())
            except Exception as e:
                print(f"Error al insertar facturas en la base de datos: {e}")

    # Cerrar la conexión con la base de datos
    db.client.close()
