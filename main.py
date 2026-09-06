import flet as ft
from flet_webview import JavaScriptMode, WebView

MAP_URL = "https://dev.kartfak.ru/miigaik_plan/#map=17.5/55.763893/37.66197/122/48&l=2"
SCHEDULE_URL = "https://study.miigaik.ru/?groupId=2050"

TAB_MAP = 0
TAB_SCHEDULE = 1

TOP_OFFSET = 56


class WebTab:
    def __init__(self, page: ft.Page, url: str):
        self._page = page
        self._url = url
        self._configured = False

        self._loader = ft.Container(
            content=ft.ProgressRing(),
            expand=True,
            alignment=ft.Alignment(0, 0),
            visible=True,
            ignore_interactions=True,
        )

        self._webview = WebView(
            url="about:blank",
            expand=True,
            on_page_started=self._on_page_started,
            on_page_ended=self._on_page_ended,
        )

        body_stack = ft.Stack(
            controls=[self._webview, self._loader],
            expand=True,
        )

        self.content = ft.Column(
            controls=[
                ft.Container(height=TOP_OFFSET),
                body_stack,
            ],
            expand=True,
            spacing=0,
        )

    async def _on_page_started(self, e):
        self._loader.visible = True
        self._page.update()
        await self._configure()

    def _on_page_ended(self, e):
        self._loader.visible = False
        self._page.update()

    async def _configure(self):
        if self._configured:
            return
        self._configured = True
        await self._webview.set_javascript_mode(JavaScriptMode.UNRESTRICTED)
        await self._webview.enable_zoom()
        await self._webview.load_request(self._url)


def build_tab_content(page: ft.Page, url: str):
    return WebTab(page, url).content


def build_navigation_bar(on_change):
    return ft.NavigationBar(
        selected_index=TAB_MAP,
        on_change=on_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.MAP,
                selected_icon=ft.Icons.MAP,
                label="Карта",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALENDAR_MONTH,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Расписание",
            ),
        ],
    )


def main(page: ft.Page):
    page.title = "Rowgaik"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0
    page.spacing = 0

    current_tab = TAB_MAP
    content_area = ft.Container(expand=True)

    def url_for_tab(tab):
        return MAP_URL if tab == TAB_MAP else SCHEDULE_URL

    def switch_tab(tab):
        nonlocal current_tab
        current_tab = tab
        content_area.content = build_tab_content(page, url_for_tab(tab))
        page.update()

    def on_nav_change(e):
        new_tab = e.control.selected_index
        if new_tab != current_tab:
            switch_tab(new_tab)

    page.navigation_bar = build_navigation_bar(on_nav_change)

    switch_tab(current_tab)
    page.add(content_area)


if __name__ == "__main__":
    ft.run(main=main)
