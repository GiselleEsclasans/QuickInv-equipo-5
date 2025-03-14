import flet as ft
from view_main import crear_appbar

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"
DARK_BLUE = "#1E0039"


def crear_vista_analisis(page: ft.Page):

    graph_view = ft.Container(
        col=6,
        bgcolor=PURPLE,
        border_radius=10,
        content=ft.Text(
            "(Gráfico aquí)",
            color=ft.Colors.WHITE,
            size=24,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=20,
        width=400,
        height=400,
        alignment=ft.alignment.center
    )


    def change_graph(text):
       
        graph_view.content = ft.Text(
            text,
            color=ft.Colors.WHITE,
            size=24,
            text_align=ft.TextAlign.CENTER,
        )
        page.update()  

   
    button_hourly_sales = ft.ElevatedButton(
        text="Ventas/Hora",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph( "Ventas/Hora")  
    )

    button_daily_sales = ft.ElevatedButton(
        text="Ventas/Día",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph( "Ventas/Día") 
    )

    button_financial_performance = ft.ElevatedButton(
        text="Desempeño Financiero",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph( "Desempeño Financiero")  
    )

    button_critical_hours = ft.ElevatedButton(
        text="Horarios Críticos",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph( "Horarios Críticos")  
    )


    button_container = ft.Row(
        controls=[
            button_hourly_sales,
            button_daily_sales,
            button_financial_performance,
            button_critical_hours
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    data_view = ft.Container(
        col=5,
        bgcolor=DARK_BLUE,
        border_radius=10,
        content=ft.Text(
            "(Datos aquí)",
            color=ft.Colors.WHITE,
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
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/analysis"),
        controls=[
            button_container,  
            ft.ResponsiveRow(
                controls=[
                    graph_view,
                    data_view
                ],
                alignment=ft.alignment.center,
                spacing=30
            )
        ],
    )