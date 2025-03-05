# view_inventory.py
import flet as ft
from model_data import DataModel
from view_main import crear_appbar
from model_data import DataModel

DARK_PURPLE = "#4A1976"
PURPLE = "#682471"
GRAY = "#D9D9D9"

data_model = DataModel()

def crear_vista_inventario(page: ft.Page) -> ft.View:
    """
    Vista Inventario con:
    - Barra de búsqueda
    - Paneles de expansión por categoría (scroll con Column)
    - Campo resumen: "Se encontraron X productos..."
    - Cada producto con Ajuste y "Guardar cambios"
    - Botón "Recargar Inventario"
    """

    # Texto que resume cuántos productos se muestran
    summary_label = ft.Text("", size=14, color=PURPLE)

    buscador_textfield = ft.TextField(
        hint_text="Buscar producto...",
        expand=True,
        border=ft.InputBorder.NONE,
        color=DARK_PURPLE,
    )

    paneles_categorias = ft.ExpansionPanelList(expand=True)

    # Envolvemos en un Column con scroll
    scroll_column = ft.Column(
        controls=[summary_label, paneles_categorias],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=5
    )

    def construir_fila_producto(prod):
        cantidad_label = ft.Text(str(prod["cantidad_disponible"]), size=14, color=DARK_PURPLE)
        ajuste_input = ft.TextField(width=50, hint_text="+5 / -2 / 3", color=DARK_PURPLE)

        def guardar_cambios(e):
            ajuste_str = ajuste_input.value.strip()
            if not ajuste_str:
                return
            if ajuste_str.startswith("+"):
                ajuste_str = ajuste_str[1:]
            try:
                ajuste_val = int(ajuste_str)
                cant_actual = int(cantidad_label.value)
                nueva_cant = cant_actual + ajuste_val
                if nueva_cant < 0:
                    print("[ERROR] Ajuste resultaría en inventario negativo.")
                    return
                data_model.actualizar_inventario_cantidad(prod["id_producto"], nueva_cant)
                cantidad_label.value = str(nueva_cant)
                cantidad_label.update()
                ajuste_input.value = ""
                ajuste_input.update()
                print("[DEBUG] Cambios guardados en producto:", prod["id_producto"])
            except ValueError:
                print("[ERROR] Ajuste no es un número válido.")

        btn_guardar = ft.ElevatedButton("Guardar cambios", icon=ft.icons.SAVE, on_click=guardar_cambios)

        return ft.Row(
            controls=[
                ft.Text(prod["nombre_producto"], size=14),
                ft.Text("Cant:", size=12),
                cantidad_label,
                ft.Text("Ajuste:", size=12),
                ajuste_input,
                btn_guardar
            ],
            spacing=5
        )

    def construir_paneles(filtrar_texto=None):
        expansions = []
        total_productos = 0  # Para contar cuántos productos se muestran en total

        cats = data_model.get_categorias()
        for cat in cats:
            col_productos = ft.Column(spacing=5)
            prods = data_model.get_inventario_de_categoria(cat)

            # Filtrar si es necesario
            if filtrar_texto:
                txt_lower = filtrar_texto.lower()
                prods = [p for p in prods if txt_lower in p["nombre_producto"].lower()]

            if not prods:
                continue

            for p in prods:
                total_productos += 1
                fila_prod = construir_fila_producto(p)
                col_productos.controls.append(fila_prod)

            expansions.append(
                ft.ExpansionPanel(
                    header=ft.Text(cat, size=16, weight=ft.FontWeight.BOLD, color=PURPLE),
                    content=col_productos,
                    expanded=False
                )
            )

        return expansions, total_productos

    def actualizar_vista(filtro=None):
        """
        Construye los paneles con o sin filtro,
        asigna expansions al paneles_categorias,
        actualiza el summary_label con la cuenta de productos.
        """
        expansions, total = construir_paneles(filtro)
        paneles_categorias.controls = expansions
        summary_label.value = f"Se encontraron {total} productos."
        page.update()  # refrescar la vista entera

    # Llamamos la primera vez sin filtro
    actualizar_vista()

    def buscar_producto(e):
        texto_busqueda = buscador_textfield.value.strip()
        actualizar_vista(filtro=texto_busqueda)

    def recargar_inventario(e):
        buscador_textfield.value = ""  # limpamos el buscador si quieres
        actualizar_vista()
        print("[DEBUG] Inventario recargado manualmente.")

    btn_buscar = ft.IconButton(icon=ft.icons.SEARCH, on_click=buscar_producto)
    btn_recargar = ft.ElevatedButton("Recargar Inventario", icon=ft.icons.REFRESH, on_click=recargar_inventario)

    # Barra de búsqueda
    buscador_row = ft.Container(
        width=500,
        border_radius=40,
        bgcolor=GRAY,
        padding=10,
        content=ft.Row(
            controls=[buscador_textfield, btn_buscar],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

    barra_busqueda = ft.Column(
        controls=[buscador_row],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    # Columna principal
    columna_principal = ft.Column(
        controls=[
            barra_busqueda,
            btn_recargar,
            scroll_column  # con summary_label y paneles_categorias
        ],
        spacing=20,
        expand=True
    )

    vista_inventario = ft.View(
        route="/inventory",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/inventory"),
        controls=[columna_principal],
    )

    return vista_inventario