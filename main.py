import flet as ft
from factura_view import crear_vista_facturas

def route_change(e: ft.RouteChangeEvent):
    e.page.views.clear()
    if e.route == "/facturas":
        e.page.views.append(crear_vista_facturas(e.page))
    else:
        e.page.views.append(ft.View(route=e.route, controls=[ft.Text("Ruta no reconocida")]))
    e.page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    page.go("/facturas")

if __name__ == "__main__":
    ft.app(target=main)
