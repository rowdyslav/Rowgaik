import flet as ft
from flet_webview import JavaScriptMode, WebView

def main(page: ft.Page):
    map_url = "https://dev.kartfak.ru/miigaik_plan/#map=17.5/55.763893/37.66197/122/48&l=2"
    page.title = "Карта МИИГАиК"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0
    page.spacing = 0

    progress_indicator = ft.Container(
        content=ft.ProgressRing(),
        expand=True,
        alignment=ft.Alignment(0, 0),
        visible=True,
        ignore_interactions=True
    )
    webview_configured = False

    async def configure_webview(e):
        nonlocal webview_configured
        show_loader(e)
        if webview_configured:
            return

        webview_configured = True
        await web_view.set_javascript_mode(JavaScriptMode.UNRESTRICTED)
        await web_view.enable_zoom()
        await web_view.load_request(map_url)

    web_view = WebView(
        url="about:blank",
        expand=True,
        on_page_started=configure_webview,
        on_page_ended=lambda e: show_webview(e)
    )

    def show_loader(e):
        progress_indicator.visible = True
        page.update()

    def show_webview(e):
        progress_indicator.visible = False
        page.update()

    page.add(
        ft.Column(
            controls=[
                ft.Container(height=56),
                ft.Stack(
                    controls=[
                        web_view,
                        progress_indicator
                    ],
                    expand=True
                )
            ],
            expand=True,
            spacing=0
        )
    )
if __name__ == "__main__":
    ft.run(main=main)
