import flet as ft
from model_data import DataModel
from view_main import crear_appbar

DARK_PURPLE = "#4A1976"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"
GRAY = "#D9D9D9"

data_model = DataModel()

def actualizar_cantidad(text_field, delta, id_producto):
    try:
        nueva_cantidad = max(0, int(text_field.value) + delta)
        text_field.value = str(nueva_cantidad)
        text_field.update()
        if delta > 0:
            data_model.aumentar_stock(id_producto, delta)
        else:
            data_model.disminuir_stock(id_producto, abs(delta))
    except ValueError:
        text_field.value = "0"
        text_field.update()

def crear_vista_inventario(page: ft.Page):
    productos = data_model.obtener_productos()
    lista_productos = ft.Column(spacing=10)
    
    for producto in productos:
        cantidad_text = ft.TextField(
            value=str(producto["cantidad_disponible"]),
            width=50,
            text_align=ft.TextAlign.CENTER,
            read_only=True,
            bgcolor="black",
            color="white"
        )
        
        fila_producto = ft.Container(
            bgcolor=DARK_PURPLE,
            border_radius=10,
            padding=10,
            content=ft.Row(
                controls=[
                    ft.Text(producto["nombre_producto"], color=LIGHT_PURPLE),
                    ft.Text("Unidades en Inventario:", color=GRAY),
                    cantidad_text,
                    ft.IconButton(icon=ft.icons.ADD, on_click=lambda e, ct=cantidad_text, p=producto["id_producto"]: actualizar_cantidad(ct, 1, p)),
                    ft.IconButton(icon=ft.icons.REMOVE, on_click=lambda e, ct=cantidad_text, p=producto["id_producto"]: actualizar_cantidad(ct, -1, p))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
        lista_productos.controls.append(fila_producto)
    
    return ft.View(
        route="/inventory",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/inventory"),
        controls=[
            ft.Column(
                controls=[
                    lista_productos
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        ],
    )

