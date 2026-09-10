import flet as ft
from flet_webview import JavaScriptMode, WebView
from urllib.parse import parse_qs, urlsplit

MAP_URL = "https://dev.kartfak.ru/miigaik_plan/#map=17.5/55.763893/37.66197/122/48&l=2"
SCHEDULE_URL = "https://study.miigaik.ru/?groupId={}"
MAP_DOMAIN = "map.miigaik.ru"
GROUP_STORAGE_KEY = "schedule_group_id"
DEFAULT_GROUP_ID = "2050"

TAB_MAP = 0
TAB_SCHEDULE = 1

TOP_OFFSET = 56


class WebTab:
    def __init__(self, page: ft.Page, url: str, on_map_url=None, on_url_change=None):
        self._page = page
        self._url = url
        self._on_map_url = on_map_url
        self._on_url_change_callback = on_url_change
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
            on_url_change=self._on_url_change,
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
        self._handle_url(e.data)
        self._page.update()
        await self._configure()

    async def _on_page_ended(self, e):
        self._loader.visible = False
        await self._prepare_map_links()
        self._page.update()

    def _on_url_change(self, e):
        self._handle_url(e.data)

    def _handle_url(self, url):
        if hasattr(url, "data"):
            url = url.data
        if not isinstance(url, str):
            return
        if self._on_url_change_callback:
            self._on_url_change_callback(url)
        hostname = (urlsplit(url).hostname or "").lower().rstrip(".")
        if self._on_map_url and (
            hostname == MAP_DOMAIN or hostname.endswith(f".{MAP_DOMAIN}")
        ):
            self._on_map_url(url)

    async def _configure(self):
        if self._configured:
            return
        self._configured = True
        await self._webview.set_javascript_mode(JavaScriptMode.UNRESTRICTED)
        await self._webview.enable_zoom()
        await self._webview.load_request(self._url)

    async def _prepare_map_links(self):
        await self._webview.run_javascript(
            """
            (() => {
                const prepare = () => {
                    document.querySelectorAll('a[href*="map.miigaik.ru"]').forEach((link) => {
                        link.target = '_self';
                    });
                };
                prepare();
                new MutationObserver(prepare).observe(document.body, {
                    childList: true,
                    subtree: true,
                });
            })();
            """
        )


def build_tab_content(page: ft.Page, url: str, on_map_url=None, on_url_change=None):
    return WebTab(
        page,
        url,
        on_map_url=on_map_url,
        on_url_change=on_url_change,
    ).content


def build_navigation_bar(on_change, on_schedule_long_press):
    schedule_icon = ft.GestureDetector(
        content=ft.Icon(ft.Icons.CALENDAR_MONTH),
        on_long_press=on_schedule_long_press,
    )
    selected_schedule_icon = ft.GestureDetector(
        content=ft.Icon(ft.Icons.CALENDAR_MONTH),
        on_long_press=on_schedule_long_press,
    )
    return ft.NavigationBar(
        selected_index=TAB_MAP,
        on_change=lambda e: on_change(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.MAP,
                selected_icon=ft.Icons.MAP,
                label="Карта",
            ),
            ft.NavigationBarDestination(
                icon=schedule_icon,
                selected_icon=selected_schedule_icon,
                label="Расписание",
            ),
        ],
    )


async def main(page: ft.Page):
    page.title = "Rowgaik"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0
    page.spacing = 0

    current_tab = TAB_MAP
    preferences = ft.SharedPreferences()
    group_id = await preferences.get(GROUP_STORAGE_KEY)
    group_id = str(group_id or DEFAULT_GROUP_ID)
    current_schedule_url = SCHEDULE_URL.format(group_id)
    content_area = ft.Container(
        expand=True,
        animate_offset=300,
        offset=ft.Offset(0, 0),
    )

    navigation_bar = None

    def url_for_tab(tab):
        return MAP_URL if tab == TAB_MAP else SCHEDULE_URL.format(group_id)

    def handle_schedule_url(url):
        nonlocal current_schedule_url
        current_schedule_url = url

    def switch_tab(tab, url=None, animate=False):
        nonlocal current_tab
        current_tab = tab
        navigation_bar.selected_index = tab
        if animate:
            content_area.offset = ft.Offset(-1, 0)
            page.update()
        content_area.content = build_tab_content(
            page,
            url or url_for_tab(tab),
            on_map_url=handle_map_url if tab == TAB_SCHEDULE else None,
            on_url_change=handle_schedule_url if tab == TAB_SCHEDULE else None,
        )
        if animate:
            content_area.offset = ft.Offset(0, 0)
        page.update()

    def handle_map_url(url):
        if current_tab != TAB_SCHEDULE:
            return
        switch_tab(TAB_MAP, url=url, animate=True)

    async def save_schedule_group(e):
        nonlocal group_id
        if current_tab != TAB_SCHEDULE:
            return
        group_id = parse_qs(urlsplit(current_schedule_url).query).get(
            "groupId", [None]
        )[0]
        if group_id:
            await preferences.set(GROUP_STORAGE_KEY, group_id)
            page.show_dialog(ft.SnackBar(ft.Text(f"Группа {group_id} сохранена")))

    def on_nav_change(new_tab):
        if new_tab != current_tab:
            switch_tab(new_tab)

    navigation_bar = build_navigation_bar(on_nav_change, save_schedule_group)
    page.navigation_bar = navigation_bar
    switch_tab(current_tab)
    page.add(content_area)


if __name__ == "__main__":
    ft.run(main=main)
