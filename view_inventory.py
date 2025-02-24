# view_inventory.py
import flet as ft
from view_main import crear_appbar
from model_data import DataModel
from datetime import datetime

DARK_PURPLE = "#4A1976"
PURPLE = "#682471"
GRAY = "#D9D9D9"

data_model = DataModel()

def crear_vista_inventario(page: ft.Page) -> ft.View:
    """
    Vista de Inventario con:
    1. Barra de búsqueda funcional (almacenada en un TextField).
    2. Paneles de expansión por categoría, con su stock y "Guardar cambios".
    3. Botón "Recargar Inventario" para regenerar la vista desde la BD.
    """

    # 1. Creamos un TextField para el buscador
    buscador_textfield = ft.TextField(
        hint_text="Escribe el nombre del producto que buscas...",
        expand=True,
        border=ft.InputBorder.NONE,
        color=DARK_PURPLE,
    )

    def buscar_producto(e):
        """
        Captura el texto ingresado en 'buscador_textfield.value'
        y filtra los productos que coincidan con ese texto.
        """
        texto_busqueda = buscador_textfield.value.strip().lower()
        print("[DEBUG] Buscando producto con texto:", texto_busqueda)

        # Reconstruimos expansions, pero filtrando
        expansions_filtrados = []
        cats = data_model.get_categorias()
        for cat in cats:
            productos_de_cat = data_model.get_inventario_de_categoria(cat)
            # Filtra los productos cuyo nombre contenga 'texto_busqueda'
            productos_filtrados = []
            for p in productos_de_cat:
                nombre_prod = p["nombre_producto"].lower()
                if texto_busqueda in nombre_prod:
                    productos_filtrados.append(p)

            # Si no hay productos filtrados, no agregamos la categoría
            if not productos_filtrados:
                continue

            cont_productos = ft.Column(spacing=5)
            for prod in productos_filtrados:
                fila = construir_fila_producto(prod)
                cont_productos.controls.append(fila)

            expansions_filtrados.append(
                ft.ExpansionPanel(
                    header=ft.Text(cat, size=16, weight=ft.FontWeight.BOLD, color=PURPLE),
                    content=cont_productos,
                    expanded=False
                )
            )

        paneles_categorias.controls = expansions_filtrados
        # No llamamos paneles_categorias.update() para evitar error
        print("[DEBUG] Búsqueda completada. Se encontraron paneles:", len(expansions_filtrados))

    # 2. IconButton y la Row para el buscador
    btn_buscar = ft.IconButton(
        icon=ft.icons.SEARCH,
        icon_color=PURPLE,
        on_click=buscar_producto  # llama buscar_producto al dar click
    )

    buscador_row = ft.Container(
        width=500,
        border_radius=40,
        bgcolor=GRAY,
        padding=10,
        content=ft.Row(
            controls=[
                buscador_textfield,
                btn_buscar
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
    )

    barra_busqueda = ft.Column(
        controls=[buscador_row],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    # 3. ExpansionPanelList
    paneles_categorias = ft.ExpansionPanelList(expand=True)

    def construir_fila_producto(prod):
        """Construye la fila con la cantidad actual, el TextField ajuste y el botón 'Guardar cambios'."""
        cantidad_label = ft.Text(str(prod["cantidad_disponible"]), size=14, color=DARK_PURPLE)
        ajuste_input = ft.TextField(width=60, hint_text="+5 / -2 / 3", color=DARK_PURPLE)

        def guardar_cambios(e):
            """Lee el ajuste y aplica."""
            ajuste_str = ajuste_input.value.strip()
            if not ajuste_str:
                return
            # quita '+' inicial
            if ajuste_str.startswith("+"):
                ajuste_str = ajuste_str[1:]
            try:
                ajuste_val = int(ajuste_str)
                cantidad_actual = int(cantidad_label.value)
                nueva_cantidad = cantidad_actual + ajuste_val
                if nueva_cantidad < 0:
                    print("[ERROR] No se permite inventario negativo.")
                    return
                data_model.actualizar_inventario_cantidad(prod["id_producto"], nueva_cantidad)
                cantidad_label.value = str(nueva_cantidad)
                cantidad_label.update()
                ajuste_input.value = ""
                ajuste_input.update()
                print("[DEBUG] Cambios guardados en producto:", prod["id_producto"])
            except ValueError:
                print("[ERROR] Ajuste no es un número válido.")

        btn_guardar = ft.ElevatedButton(
            text="Guardar cambios",
            icon=ft.icons.SAVE,
            on_click=guardar_cambios
        )

        fila = ft.Row(
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
        return fila

    def construir_paneles():
        """Genera expansions con TODAS las categorías y productos (sin filtrar)."""
        expansions = []
        cats = data_model.get_categorias()
        for cat in cats:
            col_productos = ft.Column(spacing=5)
            prods = data_model.get_inventario_de_categoria(cat)
            for p in prods:
                fila_prod = construir_fila_producto(p)
                col_productos.controls.append(fila_prod)

            expansions.append(
                ft.ExpansionPanel(
                    header=ft.Text(cat, size=16, weight=ft.FontWeight.BOLD, color=PURPLE),
                    content=col_productos,
                    expanded=False
                )
            )
        return expansions

    # Cargamos inicialmente
    paneles_categorias.controls = construir_paneles()

    def recargar_inventario(e):
        """Recarga la lista completa de inventario."""
        paneles_categorias.controls = construir_paneles()
        print("[DEBUG] Inventario recargado manualmente.")

    btn_recargar = ft.ElevatedButton(
        text="Recargar Inventario",
        icon=ft.icons.REFRESH,
        on_click=recargar_inventario
    )

    # Armamos la vista
    vista_inventario = ft.View(
        route="/inventory",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/inventory"),
        controls=[
            ft.Column(
                controls=[
                    barra_busqueda,       # Tu buscador
                    btn_recargar,         # Recargar
                    paneles_categorias    # Paneles
                ],
                spacing=20,
                expand=True
            )
        ],
    )

    return vista_inventario
