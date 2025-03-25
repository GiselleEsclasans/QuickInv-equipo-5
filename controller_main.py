# main_controller.py
import flet as ft
import pandas as pd
from model_data import DataModel
from controller_bill import procesar_facturas  
from view_main import crear_appbar
from view_analysis import crear_vista_analisis
from view_inventory import crear_vista_inventario
from view_history import crear_vista_historial  # ✅ Integración del historial

DARK_PURPLE = "#4A1976"
PURPLE = "#682471"

data_model = DataModel()  # ✅ Instancia del modelo de datos

def route_change_step_5(e: ft.RouteChangeEvent):
    """✅ Maneja los cambios de vista en la aplicación."""
    try:
        print(f"[DEBUG] route_change_step_5 con route={e.route}")
        while len(e.page.views) > 1:
            e.page.views.pop()  # ✅ Eliminar vistas anteriores 

        ''''rutas = {
            "/": lambda page=e.page: page.views.append(crear_vista_principal(page)),
            "/analysis": lambda page=e.page: page.views.append(crear_vista_analisis(page)),
            "/inventory": lambda page=e.page: page.views.append(crear_vista_inventario(page)),
            "/history": lambda page=e.page: page.views.append(crear_vista_historial(page)),  
        }'''

        rutas = {
            "/": crear_vista_principal,
            "/analysis": crear_vista_analisis,
            "/inventory": crear_vista_inventario,
            "/history": crear_vista_historial,
        }

        if e.route in rutas:
            print(f"[DEBUG] Cargando vista: {e.route}")
            nueva_vista = rutas[e.route](e.page) # ✅ Cargar la vista correspondiente
            e.page.views.clear()
            e.page.views.append(nueva_vista)
            e.page.update()
        else:
            print(f"[ERROR] Ruta desconocida: {e.route}")
            e.page.views.append(ft.View(route=e.route, controls=[ft.Text("Ruta no reconocida")]))  
            e.page.update()

    except Exception as ex:
        print(f"[ERROR] Error al cambiar de ruta: {ex}")



def crear_vista_principal(page: ft.Page):
    """✅ Vista principal con opción para cargar facturas."""
    return ft.View(
        route="/",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/"),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Image(
                            src="assets/Facturas.png",
                            width=500,
                            height=400,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        ft.Text(
                            "¡Bienvenido!",
                            size=50,
                            style=ft.TextStyle(italic=True),
                            color=DARK_PURPLE,
                        ),
                        ft.Text(
                            "Arrastra un archivo .xlsx o presiona \"Cargar Factura\"",
                            size=18,
                            color=PURPLE,
                        ),
                        ft.ElevatedButton(
                            "Cargar Factura",
                            icon=ft.Icons.UPLOAD_FILE,
                            icon_color="#FFFFFF",
                            bgcolor=DARK_PURPLE,
                            color=ft.Colors.WHITE,
                            on_click=lambda _: page.file_picker.pick_files(allow_multiple=False),
                            style=ft.ButtonStyle(
                                color={"": "#FFFFFF"},
                                bgcolor={"": "#8835D0", "hovered": "#B06EEB"},
                                padding=16,
                                elevation={"": 4},
                            )
                        ),                    
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )
        ]
    )

def main_step_5(page: ft.Page):
    """✅ Configura la aplicación y gestiona los eventos principales."""
    print("[DEBUG] Entré a main_step_5")
    page.title = "Bienvenido a QuickInv!"  # ✅ Título de la página
    page.padding = 0 # ✅ Sin relleno
    page.margin = 0 # ✅ Sin margen
    page.on_route_change = route_change_step_5 # ✅ Manejar cambios de ruta
    page.window.maximized = True

    page.file_picker = ft.FilePicker(
        on_result=lambda result: on_file_picked_step_5(result.files, page)
    )
    page.overlay.append(page.file_picker)  # ✅ Se añade a la UI
    
    if not page.route:
        page.go("/")
    else:
        page.go(page.route)

    page.update()


def on_file_picked_step_5(files, page: ft.Page):
    """✅ Procesa el archivo seleccionado y lo inserta en MongoDB Atlas."""
    print("[DEBUG] Archivos seleccionados:", files)

    if not files or not files[0].path:
        print("[DEBUG] No se seleccionó archivo o ruta nula.")

        def closeNull(e):
            page.close(dlgNull)

        dlgNull = ft.AlertDialog(
            title=ft.Text("Error al procesar archivo", color="#000000"),
            content=ft.Text("No se seleccionó ningún archivo válido.", color="#000000"),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=closeNull,
                    style=ft.ButtonStyle(
                        color={"": "#FFFFFF"},
                        bgcolor={"": "#8835D0", "hovered": "#B06EEB"}
                    )
                ),
            ],
            bgcolor="#eeeeee"
        )

        page.open(dlgNull)
        page.update()
        return

    file_path = files[0].path
    print(f"[DEBUG] Procesando archivo: {file_path}")

    errores = []
    try:
        # ✅ Procesar e insertar las facturas en MongoDB Atlas
        procesar_facturas([file_path], errores)

        def closeSuccess(e):
            page.close(dlgSuccess)

        if len(errores) == 0:
            contenido = ft.Text(f"Archivo '{files[0].name}' procesado correctamente.\nFacturas insertadas en el sistema.", color="#000000")
        else:
            erroresText = [
                ft.Text(f"Archivo '{files[0].name}' procesado parcialmente.\nFacturas insertadas en el sistema.", color="#000000"),
                ft.Text("Errores:", color="#000000", weight=ft.FontWeight.W_600, size=16)
            ]

            for error in errores:
                erroresText.append(ft.Text(f"Producto {error["Producto"]} - {error["Tipo_Error"]}", color="#000000"))

            contenido = ft.Column(erroresText)

        dlgSuccess = ft.AlertDialog(
            title=ft.Text("Procesamiento exitoso", color="#000000", weight=ft.FontWeight.W_800),
            # content=ft.Text(mensaje, color="#000000"),
            content=contenido,
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=closeSuccess,
                    style=ft.ButtonStyle(
                        color={"": "#FFFFFF"},
                        bgcolor={"": "#8835D0", "hovered": "#B06EEB"}
                    )
                ),
            ],
            bgcolor="#eeeeee"
        )

        page.open(dlgSuccess)

    except Exception as ex:
        print(f"[DEBUG] Error al procesar archivo: {type(ex).__name__} - {ex}")

        error = "Error"
        match type(ex).__name__:
            case "UnboundLocalError":
                error = "El formato de columnas es incorrecto"
            case _:
                error = "Hubo un error. Inténtelo más tarde"

        def closeError(e):
            page.close(dlgError)

        dlgError = ft.AlertDialog(
            title=ft.Text("Error al procesar archivo", color="#000000"),
            # content=ft.Text(str(ex), color="#000000")
            content=ft.Text(error, color="#000000"),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=closeError,
                    style=ft.ButtonStyle(
                        color={"": "#FFFFFF"},
                        bgcolor={"": "#8835D0", "hovered": "#B06EEB"}
                    )
                ),
            ],
            bgcolor="#eeeeee"
        )
        
        page.open(dlgError)

    page.update()


if __name__ == "__main__":
    ft.app(target=main_step_5, assets_dir="assets")
