import flet as ft
from view_main import crear_appbar

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"
DARK_BLUE = "#1E0039"

def resizeComponent(container: ft.Container, page: ft.Page):
    container.height = (page.height * 0.85),
    container.width = (page.width * 0.15)

def crear_vista_analisis(page: ft.Page):
    option_view = ft.Container(
        widthPercent = 0.15,
        heightPercent = 0.85,

        col = 1,
        bgcolor=DARK_PURPLE_2,

        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Horarios Críticos",
                            color=ft.colors.WHITE,
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            rotate=ft.Rotate(angle=-1.57),
                        ),
                        bgcolor=DARK_PURPLE_2,
                        style=ft.ButtonStyle(
                            overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                        ),
                        elevation=0,
                        
                    ),
                    padding=10,
                    bgcolor=DARK_PURPLE_2,
                    
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Desempeño Financiero",
                            color=ft.colors.WHITE,
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            rotate=ft.Rotate(angle=-1.57),
                        ),
                        bgcolor=DARK_PURPLE_2,
                        style=ft.ButtonStyle(
                            overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                        ),
                        elevation=0,
                     
                    ),
                    padding=10,
                    bgcolor=DARK_PURPLE_2,
                
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Ventas/Día",
                            color=ft.colors.WHITE,
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            rotate=ft.Rotate(angle=-1.57),
                        ),
                        bgcolor=DARK_PURPLE_2,
                        style=ft.ButtonStyle(
                            overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                        ),
                        elevation=0,
                       
                    ),
                    padding=10,
                    bgcolor=DARK_PURPLE_2,
                    
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Ventas/Hora",
                            color=ft.colors.WHITE,
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            rotate=ft.Rotate(angle=-1.57),
                        ),
                        bgcolor=DARK_PURPLE_2,
                        style=ft.ButtonStyle(
                            overlay_color=ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                        ),
                        elevation=0,
                       
                    ),
                    padding=10,
                    bgcolor=DARK_PURPLE_2,
                  
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
        ),
        padding=5,
        border_radius=ft.border_radius.only(top_right=10, bottom_right=10),
    )

    graph_view = ft.Container(
        widthPercent = 0.60,
        heightPercent = 0.85,
        col = 6,
        bgcolor=LIGHT_PURPLE,
        border_radius=10,
        content=ft.Text(
            "(Gráfico aquí)",
            color=ft.colors.WHITE,
            size=24,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=20,
        width=400,
        height=400,
        alignment=ft.alignment.center
    )

    data_view = ft.Container(
        widthPercent = 0.20,
        heightPercent = 0.85,
        col = 5,
        bgcolor=DARK_BLUE,
        border_radius=10,
        content=ft.Text(
            "(Datos aquí)",
            color=ft.colors.WHITE,
            size=24,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=20,
        width=400,
        height=400,
        alignment=ft.alignment.center
    )

    return ft.View(
        route="/analysis",
        bgcolor=ft.colors.WHITE,
        appbar=crear_appbar(page, current_route="/analysis"),
        controls=[
            ft.ResponsiveRow(
                controls=[
                    option_view,
                    graph_view,
                    data_view
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=30
            )
        ],
    )
