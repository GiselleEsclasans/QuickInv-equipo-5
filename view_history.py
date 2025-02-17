import flet as ft
from view_main import crear_appbar

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"
GRAY = "#D9D9D9"

def crear_vista_historial(page: ft.Page):
    return ft.View(
        route="/history",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/history"),
        controls=[
            ft.Column(
                
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        ],
    )