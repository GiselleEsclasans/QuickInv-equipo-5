# main_view.py
import flet as ft
from model_data import DataModel

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"

def crear_appbar(page: ft.Page, current_route: str = "/") -> ft.Container:
    def get_color(route: str, target_route: str) -> str:
        return PURPLE if route == target_route else DARK_PURPLE

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Inicio",
                                on_click=lambda _: page.go("/"),
                                icon=ft.icons.HOME,
                                bgcolor=get_color(current_route, "/"),
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                                ),
                                elevation=0,
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=get_color(current_route, "/"),
                            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
                        ),
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Historial",
                                on_click=lambda _: page.go("/history"),
                                bgcolor=get_color(current_route, "/history"),
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                                ),
                                elevation=0,
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=get_color(current_route, "/recohistoryrd"),
                            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
                        ),
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Inventario",
                                on_click=lambda _: page.go("/inventory"),
                                bgcolor=get_color(current_route, "/inventory"),
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                                ),
                                elevation=0,
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=get_color(current_route, "/inventory"),
                            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
                        ),
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Análisis de Datos",
                                icon=ft.Icons.INSIGHTS,
                                on_click=lambda _: page.go("/analysis"),
                                bgcolor=get_color(current_route, "/analysis"),
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                                ),
                                elevation=0,
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=get_color(current_route, "/analysis"),
                            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
                        ),
                    ],
                ),
                ft.Container(
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text("QuickInv", color=ft.colors.WHITE, size=30),
                    padding=ft.padding.only(right=20),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=DARK_PURPLE,
        border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
        margin=ft.margin.all(0),
        width=page.width,
    )