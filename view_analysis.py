# view_analysis.py
import flet as ft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from view_main import crear_appbar
from model_data import DataModel

# Constantes de colores
DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
PURPLE = "#682471"
DARK_BLUE = "#1E0039"

data_model = DataModel()

# Estado global para saber qué análisis está activo.
analysis_state = {"current": "Ventas/Hora"}

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return img_base64

def crear_grafico_ventas_hora(fecha_str):
    try:
        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    except Exception:
        fecha_dt = datetime.now()
        fecha_str = fecha_dt.strftime("%Y-%m-%d")
    data = data_model.ventas_por_hora(fecha_dt)
    fig, ax = plt.subplots()
    if not data:
        ax.text(0.5, 0.5, "No hay datos para la fecha seleccionada", 
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title(f"Ventas por Hora - {fecha_str}")
        ax.set_xlabel("Hora")
        ax.set_ylabel("Cantidad Vendida")
    else:
        hours = [d[0] for d in data]
        product_names = [d[1] for d in data]
        quantities = [max(d[2], 0) for d in data]
        bars = ax.bar(hours, quantities, color="indigo")
        ax.set_title(f"Ventas por Hora - {fecha_str}")
        ax.set_xlabel("Hora")
        ax.set_ylabel("Cantidad Vendida")
        plt.xticks(rotation=90)
        for bar, prod in zip(bars, product_names):
            height = bar.get_height()
            ax.annotate(prod,
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", rotation=90, fontsize=8)
    return fig_to_base64(fig)

def crear_grafico_ventas_dia(fecha_str):
    try:
        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    except Exception:
        fecha_dt = datetime.now()
        fecha_str = fecha_dt.strftime("%Y-%m-%d")
    data = data_model.ventas_productos_por_dia(fecha_dt)
    fig, ax = plt.subplots()
    if not data:
        ax.text(0.5, 0.5, "No hay datos para la fecha seleccionada", 
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title(f"Ventas por Día - {fecha_str}")
    else:
        labels = [d[0] for d in data]
        sizes = [d[1] for d in data]
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        ax.set_title(f"Ventas por Día - {fecha_str}")
    return fig_to_base64(fig)

def crear_grafico_desempeno_financiero(granularity="mes"):
    if granularity == "mes":
        data = data_model.desempeno_financiero()
        xlabel = "Mes (YYYY-MM)"
        title = "Desempeño Financiero (Mensual)"
    else:
        data = data_model.desempeno_financiero_diario()
        xlabel = "Fecha (YYYY-MM-DD)"
        title = "Desempeño Financiero (Diario)"
    fig, ax = plt.subplots()
    if not data:
        ax.text(0.5, 0.5, "No hay datos para desempeño financiero", 
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Total Ventas")
    else:
        x = [d[0] for d in data]
        y = [d[1] for d in data]
        ax.plot(x, y, marker="o", color="green")
        ax.fill_between(x, y, color="green", alpha=0.3)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
    return fig_to_base64(fig)

def crear_grafico_horarios_criticos():
    sorted_hours, sorted_days, z_matrix = data_model.horarios_criticos()
    fig, ax = plt.subplots()
    if not sorted_hours or not sorted_days:
        ax.text(
            0.5, 0.5,
            "No hay datos para horarios críticos",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes
        )
        ax.set_title("Tiempos Críticos para Ventas")  # Título más claro
    else:
        # Dibujamos el heatmap
        cax = ax.imshow(z_matrix, cmap="OrRd", aspect="auto")
        ax.set_xticks(range(len(sorted_hours)))
        ax.set_xticklabels(sorted_hours, rotation=90)
        ax.set_yticks(range(len(sorted_days)))
        ax.set_yticklabels(sorted_days)
        ax.set_title("Tiempos Críticos para Ventas")  # Título más claro

        # (Opcional) Mostrar valores dentro de cada celda:
        for i in range(len(sorted_days)):
            for j in range(len(sorted_hours)):
                valor = z_matrix[i][j]
                ax.text(
                    j, i,
                    f"{valor:.0f}",       # formatear como entero
                    ha="center", va="center",
                    color="black", fontsize=8
                )

        # Barra de colores
        fig.colorbar(cax, ax=ax)

    return fig_to_base64(fig)


def cargar_fechas_dropdown(fecha_dropdown, page):
    fechas = data_model.obtener_facturas_por_fecha()
    fecha_dropdown.options.clear()
    if fechas:
        fechas_str = [fecha.strftime("%Y-%m-%d") for fecha in fechas]
        fecha_dropdown.options.extend([ft.dropdown.Option(f) for f in fechas_str])
        fecha_dropdown.value = fechas_str[0]
    else:
        fecha_dropdown.options.append(ft.dropdown.Option("No hay facturas"))
        fecha_dropdown.value = "No hay facturas"
    page.update()

def crear_vista_analisis(page: ft.Page):
    # Obtener la fecha más reciente de facturas de la BD
    fechas = data_model.obtener_facturas_por_fecha()
    if fechas:
        fecha_inicial = fechas[0].strftime("%Y-%m-%d")
    else:
        fecha_inicial = datetime.now().strftime("%Y-%m-%d")
    
    # Gráfico inicial: Ventas por Hora con la fecha más reciente
    img_base64 = crear_grafico_ventas_hora(fecha_inicial)
    image_control = ft.Image(src_base64=img_base64, width=600, height=400)
    
    # Dropdown para seleccionar fecha (para Ventas/Hora y Ventas/Día)
    fecha_dropdown = ft.Dropdown(
        options=[],
        value=None,
        width=250
    )
    cargar_fechas_dropdown(fecha_dropdown, page)
    fecha_dropdown.on_change = lambda e: change_graph(analysis_state["current"])
    
    # Dropdown para granularidad (solo para Desempeño Financiero)
    granularidad_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("Mensual"), ft.dropdown.Option("Diario")],
        value="Mensual",
        visible=False
    )
    granularidad_dropdown.on_change = lambda e: change_graph("Desempeño Financiero")
    
    def change_graph(analysis_type: str):
        analysis_state["current"] = analysis_type
        if analysis_type == "Ventas/Hora":
            fecha_dropdown.visible = True
            granularidad_dropdown.visible = False
            fecha_str = fecha_dropdown.value if fecha_dropdown.value else fecha_inicial
            nuevo_img = crear_grafico_ventas_hora(fecha_str)
        elif analysis_type == "Ventas/Día":
            fecha_dropdown.visible = True
            granularidad_dropdown.visible = False
            fecha_str = fecha_dropdown.value if fecha_dropdown.value else fecha_inicial
            nuevo_img = crear_grafico_ventas_dia(fecha_str)
        elif analysis_type == "Desempeño Financiero":
            fecha_dropdown.visible = False
            granularidad_dropdown.visible = True
            granularity = "mes" if granularidad_dropdown.value.lower() == "mensual" else "dia"
            nuevo_img = crear_grafico_desempeno_financiero(granularity)
        elif analysis_type == "Horarios Críticos":
            fecha_dropdown.visible = False
            granularidad_dropdown.visible = False
            nuevo_img = crear_grafico_horarios_criticos()
        else:
            nuevo_img = ""
        image_control.src_base64 = nuevo_img
        image_control.update()
        page.update()
    
    # Establecer análisis inicial
    analysis_state["current"] = "Ventas/Hora"
    
    button_hourly = ft.ElevatedButton(
        text="Ventas/Hora",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph("Ventas/Hora")
    )
    button_daily = ft.ElevatedButton(
        text="Ventas/Día",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph("Ventas/Día")
    )
    button_financial = ft.ElevatedButton(
        text="Desempeño Financiero",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph("Desempeño Financiero")
    )
    button_critical = ft.ElevatedButton(
        text="Horarios Críticos",
        bgcolor=DARK_PURPLE_2,
        color="#FFFFFF",
        on_click=lambda e: change_graph("Horarios Críticos")
    )
    
    button_container = ft.Row(
        controls=[button_hourly, button_daily, button_financial, button_critical],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    top_controls = ft.Row(
        controls=[fecha_dropdown, granularidad_dropdown],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    layout = ft.Column(
        controls=[top_controls, button_container, image_control],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True
    )
    
    return ft.View(
        route="/analysis",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/analysis"),
        controls=[layout]
    )

if __name__ == "__main__":
    analysis_state = {"current": "Ventas/Hora"}
    ft.app(target=lambda page: page.views.append(crear_vista_analisis(page)), assets_dir="assets")
