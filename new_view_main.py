import flet as ft
from _components import NavBar, DARK_PURPLE, PURPLE

class mainView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.route = "/"
        self.bgcolor = ft.colors.WHITE
        self.controls = [
            NavBar(page, 0),
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
                            font_family= page.fonts["DM_Sans_Italic"],
                            size=50,
                            style=ft.TextStyle(italic=True),
                            color=DARK_PURPLE,
                        ),
                        ft.Text(
                            "Arrastra un archivo .xlsx o presiona \"Cargar Factura\"",
                            font_family= page.fonts["DM_Sans"],
                            size=18,
                            color=PURPLE,
                        ),
                        ft.ElevatedButton(
                            "Cargar Factura",
                            icon=ft.icons.UPLOAD_FILE,
                            bgcolor=DARK_PURPLE,
                            color=ft.colors.WHITE,
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