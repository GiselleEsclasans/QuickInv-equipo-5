import flet as ft
from data_analysis import cargar_datos, calcular_estadisticas

COCA_RED = "#ED1C16"
df_global = None

def route_change(e: ft.RouteChangeEvent):
    """
    Maneja el cambio de rutas.
    e.route -> string con la ruta actual
    e.page  -> referencia a la página actual
    """
    e.page.views.clear()

    if e.route == "/":
        # Vista inicial
        e.page.views.append(
            ft.View(
                route="/",
                bgcolor=ft.colors.WHITE,
                appbar=ft.AppBar(
                    title=ft.Text(
                        "Tablero de Gestión de Inventario y Costos",
                        color=ft.colors.WHITE
                    ),
                    center_title=True,
                    bgcolor=COCA_RED,
                    actions=[
                        ft.Container(
                            content=ft.Image(src="assets/coca_cola_logo.png", width=50),
                            padding=ft.padding.only(right=20),
                        )
                    ],
                ),
                controls=[
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Bienvenido(a). Por favor, cargue su archivo Excel o CSV.",
                                size=20,
                                color=COCA_RED
                            ),
                            boton_cargar_archivo(e.page),
                        ],
                    )
                ]
            )
        )

    elif e.route == "/analysis":
        # Vista de análisis
        e.page.views.append(
            ft.View(
                route="/analysis",
                bgcolor=ft.colors.WHITE,
                appbar=ft.AppBar(
                    title=ft.Text("Resultados del Análisis", color=ft.colors.WHITE),
                    center_title=True,
                    bgcolor=COCA_RED,
                    actions=[
                        ft.Container(
                            content=ft.Image(src="assets/coca_cola_logo.png", width=50),
                            padding=ft.padding.only(right=20),
                        )
                    ],
                ),
                controls=[
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Ir al Inicio",
                                icon=ft.icons.HOME,
                                on_click=lambda _: e.page.go("/"),
                                bgcolor=COCA_RED,
                                color=ft.colors.WHITE
                            ),
                            ft.Text("  |  ", color=COCA_RED),
                            ft.ElevatedButton(
                                "Ver Análisis",
                                icon=ft.icons.ANALYTICS,
                                on_click=lambda _: mostrar_analisis(e.page),
                                bgcolor=COCA_RED,
                                color=ft.colors.WHITE
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(id="container_analisis", expand=True)
                ]
            )
        )

    e.page.update()

def view_pop(e: ft.ViewPopEvent):
    """
    Maneja el botón 'Atrás' en la aplicación.
    e.view -> la vista que se está cerrando
    e.page -> la página actual
    """
    e.page.views.pop()
    top_view = e.page.views[-1]
    e.page.go(top_view.route)

def boton_cargar_archivo(page: ft.Page):
    file_picker = ft.FilePicker(
        on_result=lambda file_result: on_file_picked(file_result.files, page)
    )
    page.overlay.append(file_picker)

    return ft.ElevatedButton(
        text="Cargar archivo CSV/Excel",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False),
        bgcolor=COCA_RED,
        color=ft.colors.WHITE
    )

def on_file_picked(files, page: ft.Page):
    global df_global

    if not files:
        return
    file_path = files[0].path

    try:
        df_global = cargar_datos(file_path)
    except Exception as e:
        page.dialog = ft.AlertDialog(
            title=ft.Text("Error al cargar archivo"),
            content=ft.Text(str(e)),
            on_dismiss=lambda _: None
        )
        page.dialog.open = True
        page.update()
        return

    # Diálogo para ir a análisis
    page.dialog = ft.AlertDialog(
        title=ft.Text("Archivo cargado con éxito."),
        content=ft.Text("Presione 'Comenzar Análisis' para ver el tablero."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo(page)),
            ft.ElevatedButton("Comenzar Análisis", on_click=lambda _: ir_a_analisis(page))
        ],
        on_dismiss=lambda _: None
    )
    page.dialog.open = True
    page.update()

def cerrar_dialogo(page: ft.Page):
    page.dialog.open = False
    page.update()

def ir_a_analisis(page: ft.Page):
    page.dialog.open = False
    page.update()
    page.go("/analysis")

def mostrar_analisis(page: ft.Page):
    global df_global

    current_view = page.views[-1]
    container_analisis = current_view.controls[-1]

    if df_global is not None:
        stats = calcular_estadisticas(df_global)
        texto_stats = (
            f"Filas: {stats['filas']}\n"
            f"Columnas: {stats['columnas']}\n"
            f"Columnas: {stats['columnas_nombres']}\n"
        )

        container_analisis.content = ft.Column([
            ft.Text(
                "Estadísticas generales:",
                weight=ft.FontWeight.BOLD,
                size=18,
                color=COCA_RED
            ),
            ft.Text(texto_stats, size=16),
            ft.Text("Más análisis y gráficos aquí...", color=ft.colors.BLACK)
        ])
    else:
        container_analisis.content = ft.Text(
            "No se ha cargado ningún archivo todavía.",
            color=COCA_RED,
            size=16
        )
    page.update()

def main(page: ft.Page):
    page.title = "Tablero de Gestión de Inventario y Costos"
    page.window.width = 1200
    page.window.height = 800

    # Asignamos los "event handlers" 
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Forzamos la ruta inicial:
    if not page.route:
        page.go("/")

    page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
