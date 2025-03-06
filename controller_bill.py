import flet as ft
import pandas as pd
from model_data import DataModel

data_model = DataModel()

class FilePopUp(ft.AlertDialog):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.title: ft.Text = ft.Text(
            None,
            font_family= "Assets/Fonts/DMSans-Regular.ttf"   
        )
        self.content: ft.Text = ft.Text(
            None,
            font_family= "Assets/Fonts/DMSans-Regular.ttf",
        )
    def assignMessage(self, scenario: str, data: dict):
        match scenario:
            case "Éxito":
                self.title.value = "¡Éxito!"
                self.content.value = f"Archivo '{data["Archivo"]}' procesado correctamente.\nFacturas insertadas en MongoDB Atlas."
            case "Error_Archivo_Nulo":
                self.title.value = "Error"
                self.content.value = "El archivo seleccionado no existe o es nulo."
            case "Error_Tipo_Archivo":
                self.title.value = "Error"
                self.content.value = f"El archivo '{data["Archivo"]}' no es de tipo '.xlsx'\n¿Seleccionaste el archivo correcto?"
            case "Error_Lectura_Excel":
                self.title.value = "Error"
                self.content.value = f"El archivo '{data["Archivo"]} es un archivo Excel ilegible.\n¿Comprobaste que funcionara?" 
            case "Error_Contenido_Excel":
                self.title.value = "Error"
                contentText: str = ""
                for error in data["Errores"]:
                    if (contentText != ""):
                        contentText += "\n"
                    match error["Tipo_Error"]:
                        case "Producto_Inexistente":
                            contentText += f"El producto {error["Producto"]}, del archivo {error["Archivo"]}, no existe en inventario."
                        case "Stock_Insuficiente":
                            contentText += f"El Stock disponible de {error["Producto"]} es de {error["Cantidad_Disponible"]}, pero en la factura {error["Archivo"]} se solicitan {error["Cantidad_Solicitada"]} unidades, lo que no es factible."
                        case "Precio_Incoherente":
                            contentText += f"En {error["Archivo"]}, se lista el precio de {error["Producto"]} como {error["Precio_Indicado"]} pero su precio real es {error["Precio_Real"]}"
                self.content.value = contentText

def fileHandler(files, page: ft.Page):
    alert = FilePopUp(page)
    if ((files == None) or (files[0].path == None)):
        alert.assignMessage("Error_Archivo_Nulo", None)
        page.open(alert)
        return
    
    failedFilePointer: int = 0
    passesFileTypeCheck = fileTypeCheck(files, failedFilePointer)
    if (passesFileTypeCheck == False):
        alert.assignMessage("Error_Tipo_Archivo", {"Archivo": files[failedFilePointer].name})
        page.open(alert)
        return
    
    failedExcelPointer: int = 0
    passesExcelReadCheck = excelIsReadableCheck(files, failedExcelPointer)
    if (passesExcelReadCheck == False):
        alert.assignMessage("Error_Lectura_Excel", {"Archivo": files[failedExcelPointer].name})
        page.open(alert)
        return

    for i in range (len(files)):
        try:
            # ✅ Procesar e insertar las facturas en MongoDB Atlas
            procesar_facturas(alert, page, files)
            mensaje = f" Archivo '{files[0].name}' procesado correctamente.\nFacturas insertadas en MongoDB Atlas."

            page.dialog = ft.AlertDialog(
                title=ft.Text("Éxito"),
                content=ft.Text(mensaje),
            )
            page.dialog.open = True

        except Exception as ex:
            print(f"[DEBUG] Error al procesar archivo: {ex}")
            page.dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(str(ex))
            )
            page.dialog.open = True
            page.update()

def fileTypeCheck(files, failedFilePointer:int) -> bool:
    validState = True
    for i in range(len(files)):
        if files[i].path.endswith('.xlsx') == False:
            failedFilePointer = i
            validState = False
            break
    return validState

def excelIsReadableCheck(files, failedFilePointer:int) -> bool:
    validState = True
    for i in range(len(files)):
        dataFrame = pd.read_excel(files[i].path)
        if (dataFrame is None):
            failedFilePointer = i
            validState = False
            break
    return validState

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


def procesar_facturas(alert: FilePopUp, page:ft.Page, files):
    """✅ Procesa archivos de facturas en `.xlsx` y descuenta stock después de la inserción en MongoDB."""
    facturas_procesadas = {}
    errors = []

    for file in files:
        print(f"[DEBUG] Procesando archivo: {file.name}")
        df = pd.read_excel(file.path)

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
                        "Archivo": file.name,
                        "Tipo_Error": "Producto_Inexistente",
                        "Producto": {id_producto}
                    })
                    continue  # No procesa la factura si el producto no existe
                
                # ✅ Verificar que haya stock suficiente
                if cantidad_vendida > producto["cantidad_disponible"]:
                    print(f"Stock insuficiente para el producto {producto['nombre_producto']} (ID: {id_producto}).")
                    print(f"   Stock disponible: {producto['cantidad_disponible']}, cantidad requerida: {cantidad_vendida}.")
                    print(f"    Factura {numero_factura} no se procesará debido a falta de stock.")
                    errors.append({
                        "Archivo": file.name,
                        "Tipo_Error": "Stock_Insuficiente",
                        "Producto": {id_producto},
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
                        "Archivo": file.name,
                        "Tipo_Error": "Precio_Incoherente",
                        "Producto": {id_producto},
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
                print(f"[ERROR] Error inesperado en {file}, fila {index + 2}, factura {numero_factura}: {e}")
                continue
    if (len(errors) > 0):
        alert.assignMessage("Error_Contenido_Excel", {"Errores": errors})
        page.open(alert)

    # ✅ Insertar facturas válidas y descontar stock
    # if facturas_procesadas:
        # data_model.insertar_facturas(list(facturas_procesadas.values()))

        # 🔹 Después de insertar las facturas, descontar stock en `inventario_col`
        # for factura in facturas_procesadas.values():
        #    for producto in factura["productos"]:
        #        data_model.descontar_stock(producto["id_producto"],producto["categoria"], producto["cantidad"], factura["fecha"])

        # print(f"\n {len(facturas_procesadas)} facturas insertadas correctamente en MongoDB Atlas.")
