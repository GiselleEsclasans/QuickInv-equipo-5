import flet as ft
from _components import NavBar, PURPLE, DARK_PURPLE
from model_data import DataModel
from datetime import datetime

data_model = DataModel()

def cargar_fechas(lista_fechas, lista_facturas, page):
    """✅ Carga las fechas disponibles en el selector después de que la UI esté lista."""
    fechas = data_model.obtener_facturas_por_fecha()

    print(f"[DEBUG] Fechas disponibles en la base de datos: {fechas}")  # ✅ Depuración

    fechas_str = [fecha.strftime("%Y-%m-%d") for fecha in fechas]  # ✅ Convertir fechas a cadenas

    lista_fechas.options.clear() # ✅ Limpiar opciones anteriores
    if fechas_str:
        lista_fechas.options.extend ([ft.dropdown.Option(fecha) for fecha in fechas_str])
        lista_fechas.value = fechas_str[0]
        page.update()  # ✅ Ahora la UI se actualiza después de cargar las fechas

        #if lista_facturas not in page.controls:
           # page.add(lista_facturas)

        cargar_facturas_por_dia(fechas_str[0], lista_facturas, page) # ✅ Cargar las facturas de la primera fecha automáticamente
    else:
        lista_fechas.options.append(ft.dropdown.Option("❌ No hay facturas disponibles"))
        lista_facturas.controls.clear()
        lista_facturas.controls.append(ft.Text("❌ No hay facturas registradas.", color=PURPLE))
        page.update()


def cargar_facturas_por_dia(fecha_str, lista_facturas, page):
    """✅ Carga las facturas de un día específico y actualiza la lista."""

    print(f"[DEBUG] Fecha seleccionada: {fecha_str}")  # ✅ Depuración para verificar la fecha seleccionada

    lista_facturas.controls.clear()

    if fecha_str and fecha_str != "❌ No hay facturas disponibles":

        fecha_datetime = datetime.strptime(fecha_str, "%Y-%m-%d")  # ✅ Convertir la cadena a un objeto de fecha

        facturas = data_model.obtener_facturas_por_dia(fecha_datetime)  # ✅ Obtener facturas del modelo

        print(f"[DEBUG] Facturas encontradas para {fecha_datetime}: {facturas}")  # ✅ Depuración

        if not facturas:
            lista_facturas.controls.append(ft.Text("❌ No hay facturas registradas en esta fecha.", color=PURPLE))
        else:
            for factura in facturas:
                lista_facturas.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"📄 Factura N° {factura['numero_factura']} - {factura['cliente']['nombre']}"),
                        on_click=lambda e, f=factura: mostrar_detalle_factura(f, page)  # ✅ Pasar factura y página
                    )
                )

    lista_facturas.update()
    page.update()

def mostrar_detalle_factura(factura, page):
    """✅ Muestra los detalles de una factura en un cuadro emergente."""

    print(f"[DEBUG] Mostrando detalles de la factura: {factura}")  # ✅ Depuración

    if not isinstance(factura, dict):
        print("[ERROR] La factura recibida no es un diccionario:", factura)
        return  # ✅ Evita errores si la factura no tiene el formato correcto

    detalle_factura = ft.Column(
        [
            ft.Text(f"📅 Fecha: {factura.get('fecha', 'N/A')}"),
            ft.Text(f"🧾 Factura N°: {factura.get('numero_factura', 'N/A')}"),
            ft.Text(f"👤 Cliente: {factura.get('cliente', {}).get('nombre', 'N/A')} (ID: {factura.get('cliente', {}).get('id_cliente', 'N/A')})"),
            ft.Divider(),
            ft.Text("🛒 Productos Comprados:", weight=ft.FontWeight.BOLD),
            ft.ListView(
                controls=[
                    ft.Text(f"- {p.get('nombre_producto', 'Producto Desconocido')} (x{p.get('cantidad', 0)}) - ${p.get('subtotal', 0.0):.2f}")
                    for p in factura.get("productos", [])
                ],
                spacing=5
            ),
            ft.Divider(),
            ft.Text(f"💰 Total: ${factura.get('total_factura', 0.0):.2f}", size=18, weight=ft.FontWeight.BOLD),
        ],
        spacing=10
    )


    dialogo_factura = ft.AlertDialog(
        title=ft.Text("📄 Detalle de Factura"),
        content=detalle_factura,
        modal = True,
        actions=[
            ft.ElevatedButton("Cerrar", on_click=lambda _: cerrar_dialogo(dialogo_factura, page))
        ],
        on_dismiss=lambda e: page.update(),
    )

  
    page.overlay.append(dialogo_factura) # ✅ Añadir el diálogo a la superposición
    page.update() # ✅ Actualizar la UI


    dialogo_factura.open = True # ✅ Mostrar el diálogo de factura
    page.update() # ✅ Actualizar la UI



def cerrar_dialogo(dialogo, page):
    """✅ Cierra el diálogo de factura y actualiza la UI."""

    dialogo.open = False
    page.update()

class historyView(ft.View):
    def __init__(self, page:ft.Page):
        super().__init__()
        self.bgcolor = ft.colors.WHITE
        self.route = "/history"

        lista_facturas = ft.ListView(
            expand=True, 
            spacing=5,  # 🔹 Reducimos el espacio entre facturas
            auto_scroll=True  
        )
        lista_fechas = ft.Dropdown(
            options=[],
            value=None,
            on_change=lambda e: cargar_facturas_por_dia(e.control.value, lista_facturas, page)
        )

        self.controls = [
            NavBar(page, 1),
            ft.Column(
                [
                    ft.Text("📅 Selecciona una fecha para ver las facturas:", size=16, color=PURPLE),
                    lista_fechas,
                    ft.Divider(color=ft.colors.GREY),
                    ft.Text("📜 Facturas del día:", size=16, weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
                    ft.Container(
                        content=lista_facturas,
                        expand=True,
                        height=400,  # 🔹 Ajustamos la altura para mostrar más facturas
                    ),
                    ft.Container(
                        content=ft.ElevatedButton("⬅ Volver", on_click=lambda _: page.go("/")),
                        padding=ft.padding.only(top=10, bottom=10),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,  # 🔹 Subimos todo más arriba
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,  # 🔹 Reducimos el espacio vertical
                expand=True,
            )
        ]
