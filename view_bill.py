import flet as ft
from controller_bill import procesar_facturas

def crear_vista_facturas(page: ft.Page):
    """Crea la vista para la carga de facturas."""
    
    def cargar_archivo(e):
        if file_picker.result.files:
            archivos = [file.path for file in file_picker.result.files]
            procesar_facturas(archivos)
            page.update()

    file_picker = ft.FilePicker(on_result=cargar_archivo)

    return ft.View(
        route="/facturas",
        controls=[
            ft.Text("Carga de Facturas", size=24),
            ft.ElevatedButton("Seleccionar Facturas", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
            ft.Divider(),
        ]
    )
