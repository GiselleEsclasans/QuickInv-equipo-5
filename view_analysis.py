import flet as ft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from view_main import crear_appbar
from model_data import DataModel
import random

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
PURPLE = "#682471"
DARK_BLUE = "#1E0039"

data_model = DataModel()
analysis_state = {"current": "Ventas/Hora"}

def generar_color_aleatorio():
    """Genera un color aleatorio en formato hexadecimal que no sea ni muy oscuro ni muy claro."""
    while True:
        # Generar un color aleatorio
        r = random.randint(100, 200)  # Rango de rojo
        g = random.randint(100, 200)  # Rango de verde
        b = random.randint(100, 200)  # Rango de azul
        color = "#{:02X}{:02X}{:02X}".format(r, g, b)
        
        # Comprobar si el color es adecuado (no muy claro ni muy oscuro)
        if not (r < 100 and g < 100 and b < 100):  # No muy oscuro
            if not (r > 200 and g > 200 and b > 200):  # No muy claro
                return color



def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return img_base64

# ===================== VENTAS/HORA =====================
def crear_grafico_ventas_hora(fecha_str):
    try:
        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    except Exception:
        fecha_dt = datetime.now()
        fecha_str = fecha_dt.strftime("%Y-%m-%d")
    
    raw_data = data_model.raw_ventas_por_hora(fecha_dt)
    data_map = {}
    
    for item in raw_data:
        hour = item["hour"]
        prod = item["producto"]
        qty = item["total"]
        if hour not in data_map:
            data_map[hour] = {}
        data_map[hour][prod] = data_map[hour].get(prod, 0) + qty
    
    final_data = []
    for hour in sorted(data_map.keys(), key=lambda h: int(h)):
        product_dict = data_map[hour]
        sorted_prods = sorted(product_dict.items(), key=lambda x: x[1], reverse=True)
        sum_total = sum(product_dict.values())
        top_list = []
        for i, (pname, val) in enumerate(sorted_prods):
            if i < 3:
                top_list.append(f"{pname}({val})")
            else:
                break
        if len(sorted_prods) > 3:
            top_list.append(f"+{len(sorted_prods)-3} more")
        top_label = ", ".join(top_list)
        final_data.append((hour, top_label, sum_total, sorted_prods))
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if not final_data:
        ax.text(0.5, 0.5, "No hay datos para la fecha seleccionada", 
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title(f"Ventas por Hora - {fecha_str}")
        ax.set_xlabel("Hora")
        ax.set_ylabel("Cantidad Vendida")
    else:
        hours = [fd[0] for fd in final_data]
        labels = [fd[1] for fd in final_data]
        totals = [fd[2] for fd in final_data]
        
        group_colors = [
            "#FF8591",
            "#C08089",
            "#A17E85",
            "#8C7D83",
            "#51797C",
            "#197676",
            "#1E6273",
            "#225570",
            "#28416D",
            "#2D2D6A",
            "#321D68",
            "#390865",
            "#3F0B66",
            "#450F68",
            "#3B0B5B",
            "#4F156A",
            "#5C1D6E",
            "#682471",
            "#712E7A",
            "#8E3899",
            "#9B3CA8",
            "#AC4FB9",
            "#B668C2"
        ]
        
        max_index = totals.index(max(totals))
        
        colors = []
        for i in range(len(totals)):
            if i == max_index:
                colors.append("#BF0603")  
            else:
                colors.append(group_colors[i % len(group_colors)])  

        bars = ax.bar(hours, totals, color=colors)
        ax.set_title(f"Ventas por Hora - {fecha_str}")
        ax.set_xlabel("Hora")
        ax.set_ylabel("Cantidad Vendida")
        plt.xticks(rotation=90)
        
        for bar, lab in zip(bars, labels):
            height = bar.get_height()
            ax.annotate(lab,
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", rotation=90, fontsize=8)
    
    return fig_to_base64(fig)

# ===================== VENTAS/DÍA =====================
def crear_grafico_ventas_dia(fecha_str):

    paleta_colores = [
        "#FF8591", "#C08089", "#A17E85", "#8C7D83",
        "#51797C", "#197676", "#1E6273", "#225570",
        "#28416D", "#2D2D6A", "#321D68", "#390865",
        "#3F0B66", "#450F68", "#3B0B5B", "#4F156A",
        "#5C1D6E", "#682471", "#712E7A", "#8E3899",
        "#9B3CA8", "#AC4FB9", "#B668C2"
    ]
    
    try:
        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    except Exception:
        fecha_dt = datetime.now()
        fecha_str = fecha_dt.strftime("%Y-%m-%d")

    data = data_model.ventas_productos_por_dia(fecha_dt)
    fig, ax = plt.subplots(figsize=(8, 6))

    if not data:
        ax.text(0.5, 0.5, "No hay datos para la fecha seleccionada",
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title(f"Ventas por Día - {fecha_str}")
    else:
        labels = [d[0] for d in data]
        sizes = [d[1] for d in data]
        total_dia = sum(sizes)

        colors = []
        for i in range(len(data)):
            if i < len(paleta_colores):
                colors.append(paleta_colores[i])
            else:
                colors.append(generar_color_aleatorio())

        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
        ax.axis("equal")
        ax.set_title(f"Ventas por Día - {fecha_str}")


        fig.text(
            0.95, 0.9,
            f"Total del día: {total_dia}",
            ha="right", va="top",
            fontsize=12, color="blue",
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
        )

    return fig_to_base64(fig)

# ===================== DESEMPEÑO FINANCIERO =====================
def crear_grafico_desempeno_financiero(granularity="mes"):
    if granularity == "mes":
        data = data_model.desempeno_financiero()
        xlabel = "Mes (YYYY-MM)"
        title = "Desempeño Financiero (Mensual)"
    else:
        data = data_model.desempeno_financiero_diario()
        xlabel = "Fecha (YYYY-MM-DD)"
        title = "Desempeño Financiero (Diario)"
    fig, ax = plt.subplots(figsize=(8,6))
    if not data:
        ax.text(0.5, 0.5, "No hay datos para desempeño financiero", 
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Total Ventas")
    else:
        x = [d[0] for d in data]
        y = [d[1] for d in data]
        total_fin = sum(y)
        ax.plot(x, y, marker="o", color="#BF0603")  
        ax.fill_between(x, y, color="#FF8591", alpha=0.3) 
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
        ax.text(0.5, 1.07, f"Total: {total_fin}", transform=ax.transAxes, ha="center", va="bottom", fontsize=10, color="blue")
    return fig_to_base64(fig)

# ===================== HORARIOS CRÍTICOS =====================
def crear_grafico_horarios_criticos(mes):
    sorted_hours, sorted_days, z_matrix = data_model.horarios_criticos2(mes)  
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if not sorted_hours or not sorted_days:
        ax.text(0.5, 0.5, "No hay datos para horarios críticos", 
                horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)
        ax.set_title("Tiempos Críticos para Ventas")
    else:
        from matplotlib.colors import LinearSegmentedColormap
        colors = ["#FADEDE", "#BF0603"]
        cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

        cax = ax.imshow(z_matrix, cmap=cmap, aspect="auto")
        ax.set_xticks(range(len(sorted_hours)))
        ax.set_xticklabels(sorted_hours, rotation=90)
        ax.set_yticks(range(len(sorted_days)))
        ax.set_yticklabels(sorted_days)
        ax.set_title("Tiempos Críticos para Ventas")
        
        for i in range(len(sorted_days)):
            for j in range(len(sorted_hours)):
                val = z_matrix[i][j]
                ax.text(j, i, f"{val:.0f}", ha="center", va="center", color="black", fontsize=8)
        
        fig.colorbar(cax, ax=ax)
    
    return fig_to_base64(fig)

# ===================== FILTRO DE FECHAS PARA ANALISIS =====================
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

# ===================== VISTA PRINCIPAL DE ANALISIS =====================
def crear_vista_analisis(page: ft.Page):
    fechas = data_model.obtener_facturas_por_fecha()
    if fechas:
        fecha_inicial = fechas[0].strftime("%Y-%m-%d")
    else:
        fecha_inicial = datetime.now().strftime("%Y-%m-%d")

    img_base64 = crear_grafico_ventas_hora(fecha_inicial)
    image_control = ft.Image(src_base64=img_base64, width=800, height=600)
    graph_container = ft.Container(content=image_control, alignment=ft.alignment.center)
    
    fecha_dropdown = ft.Dropdown(options=[], value=None, width=250)
    cargar_fechas_dropdown(fecha_dropdown, page)
    
    
    
    
    granularidad_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("Mensual"), ft.dropdown.Option("Diario")],
        value="Mensual",
        visible=False
    )
    
    mes_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(str(i)) for i in range(1, 13)],
        value="1",  
        visible=False
    )
    
    fecha_dropdown.on_change = lambda e: change_graph(analysis_state["current"])
    granularidad_dropdown.on_change = lambda e: change_graph("Desempeño Financiero")
    mes_dropdown.on_change = lambda e: update_horarios_criticos()
    
    def update_horarios_criticos():
        mes = int(mes_dropdown.value)  
        nuevo_img = crear_grafico_horarios_criticos(mes)  
        image_control.src_base64 = nuevo_img
        image_control.update()
        page.update()
    
    def change_graph(analysis_type: str):
        analysis_state["current"] = analysis_type
        if analysis_type == "Ventas/Hora":
            fecha_dropdown.visible = True
            granularidad_dropdown.visible = False
            mes_dropdown.visible = False
            fecha_str = fecha_dropdown.value or fecha_inicial
            nuevo_img = crear_grafico_ventas_hora(fecha_str)
        elif analysis_type == "Ventas/Día":
            fecha_dropdown.visible = True
            granularidad_dropdown.visible = False
            mes_dropdown.visible = False
            fecha_str = fecha_dropdown.value or fecha_inicial
            nuevo_img = crear_grafico_ventas_dia(fecha_str)
        elif analysis_type == "Desempeño Financiero":
            fecha_dropdown.visible = False
            granularidad_dropdown.visible = True
            mes_dropdown.visible = False
            granularity = "mes" if (granularidad_dropdown.value or "Mensual").lower() == "mensual" else "dia"
            nuevo_img = crear_grafico_desempeno_financiero(granularity)
        elif analysis_type == "Horarios Críticos":
            fecha_dropdown.visible = False
            granularidad_dropdown.visible = False
            mes_dropdown.visible = True
            mes = int(mes_dropdown.value) 
            nuevo_img = crear_grafico_horarios_criticos(mes) 
        else:
            nuevo_img = ""
        image_control.src_base64 = nuevo_img
        image_control.update()
        page.update()
    
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
    
    filter_container = ft.Row(
        controls=[fecha_dropdown, granularidad_dropdown, mes_dropdown],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    top_container = ft.Row(
        controls=[button_container, filter_container],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=40 
    )
    
    layout = ft.Column(
        controls=[top_container, graph_container],  
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True
    )
    
 
    layout_with_margin = ft.Container(
        content=layout,
        margin=ft.margin.only(top=20),  
        expand=True
    )
    
    return ft.View(
        route="/analysis",
        bgcolor=ft.Colors.WHITE,
        appbar=crear_appbar(page, current_route="/analysis"),
        controls=[layout_with_margin]  
    )

if __name__ == "__main__":
    analysis_state["current"] = "Ventas/Hora"
    ft.app(target=lambda page: page.views.append(crear_vista_analisis(page)), assets_dir="assets")