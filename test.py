import flet as ft
import pandas as pd

###############################################################################
# Funciones de análisis (inline o importadas de data_analysis.py)
###############################################################################
def cargar_datos(filepath: str):
    if not filepath:
        raise ValueError("La ruta del archivo es nula o vacía.")
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath)
    elif filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError("El archivo debe ser un CSV o un Excel.")


def calcular_estadisticas(df: pd.DataFrame) -> dict:
    return {
        "filas": df.shape[0],
        "columnas": df.shape[1],
        "columnas_nombres": list(df.columns),
    }

###############################################################################
#             PASO 5: VERSIÓN FINAL - Dashboard Completo
###############################################################################

COCA_RED = "#ED1C16"
df_step_5 = None  # Variable global para almacenar el DataFrame
analysis_text_5 = ft.Text("Aún no se han cargado datos.")


def route_change_step_5(e: ft.RouteChangeEvent):
    print(f"[DEBUG] route_change_step_5 con route={e.route}")
    e.page.views.clear()

    if e.route == "/":
        print("[DEBUG] Pintando vista '/' en Paso 5")
        e.page.views.append(
            ft.View(
                route="/",
                bgcolor=ft.colors.WHITE,
                appbar=ft.AppBar(
                    title=ft.Text("Dashboard de Análisis de Datos ", color=ft.colors.WHITE),
                    center_title=True,
                    bgcolor=COCA_RED,
                    actions=[
                        ft.Container(
                            content=ft.Image(src="coca_cola_logo.png", width=50),
                            padding=ft.padding.only(right=20),
                        )
                    ],
                ),
                controls=[
                    ft.Column(
                        [
                            ft.Text("Bienvenido(a). Cargue su archivo y luego vaya al análisis.", size=18),
                            ft.ElevatedButton(
                                "Cargar CSV/Excel",
                                icon=ft.icons.UPLOAD_FILE,
                                bgcolor=COCA_RED,
                                color=ft.colors.WHITE,
                                on_click=lambda _: e.page.file_picker.pick_files(allow_multiple=False)
                            ),
                            ft.ElevatedButton(
                                "Ir al análisis",
                                icon=ft.icons.ANALYTICS,
                                bgcolor=COCA_RED,
                                color=ft.colors.WHITE,
                                on_click=lambda _: e.page.go("/analysis")
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ]
            )
        )

    elif e.route == "/analysis":
        print("[DEBUG] Pintando vista '/analysis' en Paso 5")
        e.page.views.append(
            ft.View(
                route="/analysis",
                bgcolor=ft.colors.WHITE,
                appbar=ft.AppBar(
                    title=ft.Text("Resultados del Análisis (Paso 5)", color=ft.colors.WHITE),
                    center_title=True,
                    bgcolor=COCA_RED,
                    actions=[
                        ft.Container(
                            content=ft.Image(src="coca_cola_logo.png", width=50),
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
                            ft.Text("  |  ", color=ft.colors.BLACK),
                            ft.ElevatedButton(
                                "Ver Estadísticas",
                                icon=ft.icons.INSIGHTS,
                                on_click=lambda _: mostrar_analisis_step_5(e.page),
                                bgcolor=COCA_RED,
                                color=ft.colors.WHITE
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        expand=True
                    )
                ]
            )
        )
    else:
        print(f"[DEBUG] Ruta desconocida en Paso 5: {e.route}")
        e.page.views.append(
            ft.View(
                route=e.route,
                controls=[ft.Text(f"Ruta no reconocida (Paso 5): {e.route}")]
            )
        )

    e.page.update()


def view_pop_step_5(e: ft.ViewPopEvent):
    print("[DEBUG] view_pop_step_5 disparado")
    e.page.views.pop()
    if len(e.page.views) > 0:
        top_view = e.page.views[-1]
        e.page.go(top_view.route)


def on_file_picked_step_5(files, page: ft.Page):
    global df_step_5
    print("[DEBUG] on_file_picked_step_5 con files:", files)

    if not files or not files[0].path:
        print("[DEBUG] No se seleccionó archivo o ruta nula.")
        page.dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text("No se seleccionó ningún archivo válido."),
        )
        page.dialog.open = True
        page.update()
        return

    file_path = files[0].path
    print(f"[DEBUG] Cargando archivo desde ruta: {file_path}")

    try:
        # Cargamos el archivo según su extensión
        if file_path.endswith(".csv"):
            df_step_5 = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df_step_5 = pd.read_excel(file_path)
        else:
            raise ValueError("El archivo debe ser un CSV o un Excel.")

        print("[DEBUG] DataFrame cargado OK.")
        page.dialog = ft.AlertDialog(
            title=ft.Text("Éxito"),
            content=ft.Text(f"Archivo '{files[0].name}' cargado correctamente."),
        )
        page.dialog.open = True
    except Exception as ex:
        print(f"[DEBUG] Error al cargar archivo: {ex}")
        page.dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(str(ex))
        )
        page.dialog.open = True

    page.update()


def mostrar_analisis_step_5(page: ft.Page):
    global df_step_5
    # Buscamos la vista actual y su contenedor
    current_view = page.views[-1]
    if len(current_view.controls) > 0:
        contenedor_analisis = current_view.controls[-1]  # el ft.Container
        if isinstance(contenedor_analisis, ft.Container):
            if df_step_5 is not None:
                stats = calcular_estadisticas(df_step_5)
                texto_stats = (
                    f"Filas: {stats['filas']}\n"
                    f"Columnas: {stats['columnas']}\n"
                    f"Columnas nombres: {stats['columnas_nombres']}\n"
                )
                contenedor_analisis.content = ft.Text(texto_stats, size=16)
            else:
                contenedor_analisis.content = ft.Text("Aún no se ha cargado ningún archivo.")
            contenedor_analisis.update()


def main_step_5(page: ft.Page):
    print("[DEBUG] Entré a main_step_5")
    page.title = "Paso 5: Dashboard Completo"

    page.on_route_change = route_change_step_5
    page.on_view_pop = view_pop_step_5

    page.file_picker = ft.FilePicker(
        on_result=lambda result: on_file_picked_step_5(result.files, page)
    )
    page.overlay.append(page.file_picker)

    print("[DEBUG] page.route actual:", page.route)
    if not page.route:
        print("[DEBUG] No hay route, forzamos '/'")
        page.go("/")
    else:
        print(f"[DEBUG] Ya hay route={page.route}, forzamos page.go(page.route)")
        page.go(page.route)

    page.update()
    print("[DEBUG] Saliendo de main_step_5...")

###############################################################################
# EJECUCIÓN (Descomenta si quieres correr paso 5 directamente)
###############################################################################
if __name__ == "__main__":
    ft.app(target=main_step_5, assets_dir="assets")
