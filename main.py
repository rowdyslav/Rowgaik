import flet as ft
from flet_webview import JavaScriptMode, WebView

def main(page: ft.Page):
    map_url = "https://dev.kartfak.ru/miigaik_plan/#map=17.5/55.763893/37.66197/122/48&l=2"
    page.title = "Расписание МИИГАиК"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0
    page.spacing = 0

    print("[DEBUG] Приложение запущено. Инициализация элементов...")

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
        on_page_ended=lambda e: show_webview(e),
        on_web_resource_error=lambda e: show_error(e),
        on_console_message=lambda e: print(
            f"[JS {e.data}]"
        )
    )

    def show_loader(e):
        print(f"[DEBUG] Событие: on_page_started. URL: {e.data if hasattr(e, 'data') else 'unknown'}")
        progress_indicator.visible = True
        page.update()
        print("[DEBUG] Экран переключен в режим ЗАГРУЗКИ")

    def show_webview(e):
        print(f"[DEBUG] Событие: on_page_ended. Страница загружена успешно.")
        progress_indicator.visible = False
        page.update()
        print("[DEBUG] Экран переключен в режим ОТОБРАЖЕНИЯ САЙТА")

    def show_error(e):
        print(f"[ERROR] Ошибка загрузки ресурса в WebView! Детали: {e.data if hasattr(e, 'data') else e}")

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
    print("[DEBUG] Элементы добавлены на страницу. Ожидание ответа от WebView...")

if __name__ == "__main__":
    ft.run(main=main)
