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
    summary_label = ft.Text("", size=16, color=PURPLE, weight=400)

    buscador_textfield = ft.TextField(
        hint_text="Buscar producto...",
        hint_style=ft.TextStyle(
            size=15,
            color="#534D54"
        ),
        expand=True,
        border=ft.InputBorder.NONE,
        color=DARK_PURPLE,
    )

    paneles_categorias = ft.ExpansionPanelList(
        expand=True,
        expand_icon_color="#692470",
        expanded_header_padding=ft.padding.symmetric(horizontal=16),
        divider_color="#692470"
    )

    # Envolvemos en un Column con scroll
    scroll_column = ft.Column(
        controls=[summary_label, paneles_categorias],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=5
    )

    def construir_fila_producto(prod):
        cantidad_label = ft.Text("Cant: " + str(prod["cantidad_disponible"]), size=18, weight=600, color="#682471")
        ajuste_input = ft.TextField(
            width=300,
            hint_text="Ajuste: +5 / -2 / 3",
            hint_style=ft.TextStyle(
                size=15,
                color="#534D54"
            ),
            color="#682471",
            bgcolor="#CEBECE",
            border_color="#00000000"
        )

        def guardar_cambios(e):
            ajuste_str = ajuste_input.value.strip()
            if not ajuste_str:
                return
            if ajuste_str.startswith("+"):
                ajuste_str = ajuste_str[1:]
            try:
                ajuste_val = int(ajuste_str)
                cant_actual = int(cantidad_label.value.strip("Cant: "))
                nueva_cant = cant_actual + ajuste_val
                if nueva_cant < 0:
                    print("[ERROR] Ajuste resultaría en inventario negativo.")
                    return
                data_model.actualizar_inventario_cantidad(prod["id_producto"], nueva_cant)
                cantidad_label.value = "Cant: " + str(nueva_cant)
                cantidad_label.update()
                ajuste_input.value = ""
                ajuste_input.update()
                print("[DEBUG] Cambios guardados en producto:", prod["id_producto"])
            except ValueError:
                print("[ERROR] Ajuste no es un número válido.")

        btn_guardar = ft.ElevatedButton(
            "Guardar cambios",
            icon=ft.icons.SAVE,
            icon_color="#FFFFFF",
            color="#FFFFFF",
            on_click=guardar_cambios,
            bgcolor={"": "#8835D0", "hovered": "#B06EEB"})

        return ft.Row(
            controls=[
                ft.Text(
                    prod["nombre_producto"],
                    size=18,
                    weight=700,
                    color="#682471"
                ),
                cantidad_label,
                ajuste_input,
                btn_guardar
            ],
            spacing=9,
            alignment=ft.MainAxisAlignment.SPACE_AROUND
        )

    def construir_paneles(filtrar_texto=None):
        expansions = []
        total_productos = 0  # Para contar cuántos productos se muestran en total

        cats = data_model.get_categorias()
        for cat in cats:
            col_productos = ft.Column(spacing=10)
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
                    header=ft.Container(
                        content=ft.Text(
                            cat,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=PURPLE
                        ),
                        padding=ft.padding.all(16),
                        border_radius=24
                    ),
                    content=col_productos,
                    bgcolor="#EEE6F0",
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

    btn_buscar = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=buscar_producto,
        icon_color="#8934D0"
    )
    btn_recargar = ft.ElevatedButton(
        "Recargar Inventario",
        icon=ft.icons.REFRESH,
        icon_color="#FFFFFF",
        on_click=recargar_inventario,
        style=ft.ButtonStyle(
            color={"": "#FFFFFF"},
            bgcolor={"": "#8835D0", "hovered": "#B06EEB"},
            padding=12,
            elevation={"": 4},
        )
    )

    # Barra de búsqueda
    buscador_row = ft.Container(
        content=ft.Container(
            width=1000,
            border_radius=40,
            bgcolor=GRAY,
            padding=ft.padding.only(left=16),
            content=ft.Row(
                controls=[buscador_textfield, btn_buscar],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            shadow=ft.BoxShadow(
                blur_radius=5,
                color="#777777",
                # offset=ft.Offset(0, 5),
                blur_style=ft.ShadowBlurStyle.OUTER,
            ),
        ),
        padding=ft.padding.only(left=16, top=12)
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