import flet as ft
from main_view import crear_appbar

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"
GRAY = "#D9D9D9"

def buscar_producto(e):
    # Aquí puedes agregar la lógica para buscar el producto
    print("Buscando producto:", e.control.value)

def crear_vista_inventario(page: ft.Page):
    return ft.View(
        route="/inventory",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/inventory"),
        controls=[
            ft.Column(
                controls=[
                    ft.Container(
                        width=500,
                        border_radius=40,
                        bgcolor=GRAY,
                        padding=10,
                        content=ft.Row(
                            controls=[
                                ft.TextField(
                                    hint_text="Escribe el nombre del producto que buscas...",
                                    expand=True,
                                    border=ft.InputBorder.NONE,  # Sin borde
                                    color=DARK_PURPLE,
                                    text_style=ft.TextStyle(color=DARK_PURPLE),
                                    hint_style=ft.TextStyle(color=LIGHT_PURPLE),
                                    on_focus=lambda e: e.control.update(hint_text="")
                                ),
                                ft.IconButton(
                                    icon=ft.icons.SEARCH,
                                    icon_color=PURPLE,
                                    on_click=buscar_producto,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        ],
    )
