# main_controller.py
import flet as ft
import pandas as pd
from model_data import DataModel
from controller_bill import procesar_facturas  
from view_main import crear_appbar
from view_analysis import crear_vista_analisis
from view_inventory import crear_vista_inventario
from view_history import crear_vista_historial

DARK_PURPLE = "#4A1976"
PURPLE = "#682471"

data_model = DataModel()  # ✅ Instancia del modelo de datos

def route_change_step_5(e: ft.RouteChangeEvent):
    """Maneja los cambios de vista en la aplicación."""
    print(f"[DEBUG] route_change_step_5 con route={e.route}")
    e.page.views.clear()

    if e.route == "/":
        print("[DEBUG] Pintando vista '/' en Paso 5")
        e.page.views.append(
            ft.View(
                route="/",
                bgcolor=ft.Colors.WHITE,
                appbar=crear_appbar(e.page, current_route="/"),
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
                                    "Arrastra un archivo .xlsx o .csv; o presiona \"Cargar Factura\"",
                                    size=18,
                                    color=PURPLE,
                                ),
                                ft.ElevatedButton(
                                    "Cargar Factura",
                                    icon=ft.Icons.UPLOAD_FILE,
                                    bgcolor=DARK_PURPLE,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda _: e.page.file_picker.pick_files(allow_multiple=False)
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
        )

    elif e.route == "/analysis":
        print("[DEBUG] Pintando vista '/analysis' en Paso 5")
        e.page.views.append(crear_vista_analisis(e.page))
        
    elif e.route == "/record":
        print("[DEBUG] Pintando vista '/record' en Paso 5")
        e.page.views.append(crear_vista_historial(e.page))


    elif e.route == "/inventory":
        print("[DEBUG] Pintando vista '/inventory' en Paso 5")
        e.page.views.append(crear_vista_inventario(e.page))

    else:
        print(f"[DEBUG] Ruta desconocida en Paso 5: {e.route}")
        e.page.views.append(
            ft.View(
                route=e.route,
                controls=[ft.Text(f"Ruta no reconocida (Paso 5): {e.route}")]
            )
        )

    e.page.update()

def on_file_picked_step_5(files, page: ft.Page):
    """Procesa el archivo seleccionado y lo inserta en MongoDB Atlas."""
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

def main_step_5(page: ft.Page):
    """Configura la aplicación y gestiona los eventos principales."""
    print("[DEBUG] Entré a main_step_5")
    page.title = "Paso 5: Dashboard Completo"
    page.padding = 0
    page.margin = 0
    page.on_route_change = route_change_step_5

    page.file_picker = ft.FilePicker(
        on_result=lambda result: on_file_picked_step_5(result.files, page)
    )
    page.overlay.append(page.file_picker)

    if not page.route:
        page.go("/")
    else:
        page.go(page.route)

    page.update()

if __name__ == "__main__":
    ft.app(target=main_step_5, assets_dir="assets")
