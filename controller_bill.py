import pandas as pd
from model_data import DataModel

data_model = DataModel()

def validar_fila(fila, index, archivo):
    """✅ Valida los datos antes de procesarlos."""
    errores = []
    
    # Verificar que los valores no sean nulos o vacíos
    campos_obligatorios = ['Número Factura', 'Fecha', 'Hora', 'ID Producto', 'Nombre Producto', 
                           'Categoría', 'Cantidad', 'Precio Unitario', 'Subtotal', 'ID Cliente', 'Nombre Cliente']
    
    for campo in campos_obligatorios:
        if pd.isna(fila[campo]) or fila[campo] == "":
            errores.append(f"{campo} está vacío.")

    # Verificar que `Cantidad`, `Precio Unitario` y `Subtotal` sean positivos
    if fila['Cantidad'] <= 0:
        errores.append("Cantidad debe ser un número positivo.")
    if fila['Precio Unitario'] <= 0:
        errores.append("Precio unitario no puede ser negativo o cero.")
    if fila['Subtotal'] != fila['Cantidad'] * fila['Precio Unitario']:
        errores.append("Subtotal no coincide con Cantidad * Precio Unitario.")

    # ✅ Verificar que el ID Producto y Categoría existen en `inventario_col`
    producto = data_model.obtener_producto(fila['Categoría'], fila['ID Producto'])
    if not producto:
        errores.append(f"Producto con ID '{fila['ID Producto']}' no encontrado en inventario.")

    # Si hay errores, imprimirlos y devolver `False`
    if errores:
        print(f" Errores en {archivo}, fila {index + 2}: {', '.join(errores)}")
        return False, None

    return True, producto


def procesar_facturas(archivos, errors):
    """✅ Procesa archivos de facturas en `.xlsx` y descuenta stock después de la inserción en MongoDB."""
    facturas_procesadas = {}

    for archivo in archivos:
        if not archivo.endswith('.xlsx'):
            print(f"[ERROR] El archivo {archivo} no es un formato válido. Solo se aceptan `.xlsx`.")
            continue
        
        df = pd.read_excel(archivo)
        if df is None:
            print(f"[ERROR] No se pudo leer el archivo {archivo}.")
            continue

        for index, fila in df.iterrows():
            try:
                numero_factura = fila['Número Factura']
                id_producto = fila['ID Producto']
                categoria = fila['Categoría']
                cantidad_vendida = fila['Cantidad']
                precio_factura = fila['Precio Unitario']
                fecha_factura = fila['Fecha']

                # Verificar que el producto existe antes de procesar la factura
                producto = data_model.obtener_producto(categoria, id_producto)
                if not producto:
                    print(f"[ERROR] Producto '{id_producto}' no encontrado en inventario. Factura {numero_factura} no se procesará.")
                    errors.append({
                        "Archivo": archivo,
                        "Tipo_Error": "Producto_Inexistente",
                        "Producto": id_producto
                    })
                    continue  # No procesa la factura si el producto no existe
                
                # ✅ Verificar que haya stock suficiente
                if cantidad_vendida > producto["cantidad_disponible"]:
                    print(f"Stock insuficiente para el producto {producto['nombre_producto']} (ID: {id_producto}).")
                    print(f"   Stock disponible: {producto['cantidad_disponible']}, cantidad requerida: {cantidad_vendida}.")
                    print(f"    Factura {numero_factura} no se procesará debido a falta de stock.")
                    errors.append({
                        "Archivo": archivo,
                        "Tipo_Error": "Stock_Insuficiente",
                        "Producto": id_producto,
                        "Cantidad_Solicitada": cantidad_vendida,
                        "Cantidad_Disponible": producto["cantidad_disponible"]
                    })
                    continue  # ❌ No procesa la factura si no hay suficiente stock
                
                # ✅ Verificar que el precio unitario coincida con el del inventario
                precio_inventario = producto["precio_unitario"]
                if precio_factura != precio_inventario:
                    print(f" Precio incorrecto en Factura {numero_factura} para el producto {producto['nombre_producto']} (ID: {id_producto}).")
                    print(f"   Precio en inventario: {precio_inventario}, precio en factura: {precio_factura}.")
                    print(f"    Factura {numero_factura} no se procesará debido a discrepancia de precio.")
                    errors.append({
                        "Archivo": archivo,
                        "Tipo_Error": "Precio_Incoherente",
                        "Producto": id_producto,
                        "Precio_Indicado": precio_factura,
                        "Precio_Real": precio_inventario
                    })
                    continue  # ❌ No procesa la factura si el precio no coincide

                # ✅ Validar la fila antes de procesarla
                if numero_factura not in facturas_procesadas:
                    facturas_procesadas[numero_factura] = {
                        "numero_factura": numero_factura,
                        "fecha": fecha_factura,
                        "hora": fila['Hora'].strftime("%H:%M") if isinstance(fila['Hora'], pd.Timestamp) else str(fila['Hora']),
                        "cliente": {
                            "id_cliente": fila['ID Cliente'],
                            "nombre": fila['Nombre Cliente']
                        },
                        "productos": [],
                        "total_factura": 0
                    }

                # ✅ Agregar el producto a la factura
                facturas_procesadas[numero_factura]["productos"].append({
                    "id_producto": id_producto,
                    "nombre_producto": fila['Nombre Producto'],
                    "categoria": categoria,
                    "cantidad": cantidad_vendida,
                    "precio_unitario": fila['Precio Unitario'],
                    "subtotal": fila['Subtotal']
                })

                # ✅ Actualizar total de la factura
                facturas_procesadas[numero_factura]["total_factura"] += fila['Subtotal']

                print(f" Factura {numero_factura} procesada correctamente.")

            except Exception as e:
                print(f"[ERROR] Error inesperado en {archivo}, fila {index + 2}, factura {numero_factura}: {e}")
                continue

    # ✅ Insertar facturas válidas y descontar stock
    if facturas_procesadas:
        data_model.insertar_facturas(list(facturas_procesadas.values()))

        # 🔹 Después de insertar las facturas, descontar stock en `inventario_col`
        for factura in facturas_procesadas.values():
            for producto in factura["productos"]:
                data_model.descontar_stock(producto["id_producto"],producto["categoria"], producto["cantidad"], factura["fecha"])

        print(f"\n {len(facturas_procesadas)} facturas insertadas correctamente en el sistema.")
