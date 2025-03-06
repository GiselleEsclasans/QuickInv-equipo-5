import flet as ft
from new_view_main import mainView
from view_history import crear_vista_historial
from controller_bill import fileHandler

class Router():
    def __init__(self, page):
        self.routes = {
            "/": mainView(page),
            "/history": crear_vista_historial(page),
            # "/inventory" = inventoryView(),
            # "/analysis" = analysisView(),
        }

def main(page: ft.Page):
    
    page.file_picker = ft.FilePicker(
        on_result=lambda result: fileHandler(result.files, page)
    )
    page.overlay.append(page.file_picker)
    page.fonts = {
        "DM_Sans":"Assets/Fonts/DMSans-Regular.ttf",
        "DM_Sans_Italic": "Assets/Fonts/DMSans-Italic.ttf",
    }

    appRouter = Router(page)
    def routeChangeHandler(event: ft.RouteChangeEvent):
        page.views.clear()
        page.views.append(appRouter.routes[event.route])
        page.update()
    
    page.window.min_width= 700
    page.window.min_height= 700

    page.views.append(mainView(page))
    page.update()

    page.on_route_change = routeChangeHandler

ft.app(target=main)
