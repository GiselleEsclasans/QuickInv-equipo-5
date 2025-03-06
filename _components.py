import flet as ft

DARK_PURPLE = "#4A1976"
DARK_PURPLE_2 = "#390865"
LIGHT_PURPLE = "#9B5AA3"
PURPLE = "#682471"
GRAY = "#D9D9D9"

class NavBar(ft.AppBar):
    def __init__(self, page: ft.Page, currentView: int):
        super().__init__()
        self.bgcolor = DARK_PURPLE
        self.__accessList = [True, True, True, True]
        if ((0 <= currentView) and (currentView < len(self.__accessList))):
            self.__accessList[currentView] = False
        self.title = ft.Text("QuickInv", font_family=page.fonts["DM_Sans"], weight=ft.FontWeight.BOLD)
        self.leading = ft.Container(
            content=ft.Row(
                controls=[
                    self.ButtonGroup(page, "Inicio", "/", self.__accessList[0]),
                    self.ButtonGroup(page, "Historial", "/history", self.__accessList[1]),
                    self.ButtonGroup(page, "Inventario", "/inventory", self.__accessList[2]),
                    self.ButtonGroup(page, "Análisis", "/analysis", self.__accessList[3]),
                ]
            ),
        )
        self.pageRef = page
        self.leading_width = page.width-140
        page.on_resized = self.resizeAdjust
    def resizeAdjust(self, e:ft.WindowResizeEvent):
        self.leading_width = e.width-140
        self.pageRef.update()

    class ButtonGroup(ft.Container):
        def __init__(self, page: ft.Page, text: str, route: str, state: bool):
            super().__init__()
            if (state == False):
                self.border_radius = ft.border_radius.only(bottom_right=20, bottom_left=20)
                self.bgcolor = PURPLE
            else:
                self.bgcolor = DARK_PURPLE
            self.height = 60
            self.content = self.NavBarButton(page, text, route, state)
        class NavBarButton(ft.ElevatedButton):
            def __init__(self, page: ft.Page, text: str, route: str, state: bool):
                super().__init__()
                self.content = ft.Text(
                    text,
                    font_family=page.fonts["DM_Sans"]
                )
                self.font_family = page.fonts["DM_Sans"]
                self.appRoute = route
                self.pageRef = page
                self.style = ft.ButtonStyle(
                    color= ft.colors.WHITE,
                    bgcolor= {
                        ft.ControlState.DEFAULT: DARK_PURPLE,
                        ft.ControlState.HOVERED: ft.colors.with_opacity(0.5, LIGHT_PURPLE),
                        ft.ControlState.DISABLED: PURPLE
                    },
                    padding= ft.padding.symmetric(vertical=10, horizontal=30)
                )
                self.elevation = 0
                if (state == False):
                    self.disabled = True
                else:
                    self.on_click = self.changeRoute
            def changeRoute(self, e):
                self.pageRef.go(self.appRoute)
                