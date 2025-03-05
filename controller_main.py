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
                            bgcolor=DARK_PURPLE,
                            color=ft.Colors.WHITE,
                            on_click=lambda _: page.file_picker.pick_files(allow_multiple=False)
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
        page.dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text("No se seleccionó ningún archivo válido."),
        )
        page.dialog.open = True
        page.update()
        return

    file_path = files[0].path
    print(f"[DEBUG] Procesando archivo: {file_path}")

    try:
        # ✅ Procesar e insertar las facturas en MongoDB Atlas
        procesar_facturas([file_path])
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


if __name__ == "__main__":
    ft.app(target=main_step_5, assets_dir="assets")
