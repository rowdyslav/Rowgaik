import flet as ft
from flet_webview import WebView

def main(page: ft.Page):
    page.title = "Расписание МИИГАиК"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0

    print("[DEBUG] Приложение запущено. Инициализация элементов...")

    # Индикатор загрузки (центрирован)
    progress_indicator = ft.Container(
        content=ft.ProgressRing(),
        expand=True,
        visible=True  # Изначально виден
    )

    # WebView должен оставаться видимым для платформы. Если создать его с
    # visible=False, нативный WebView может не смонтироваться и события
    # on_page_started/on_page_ended никогда не будут вызваны.
    web_view = WebView(
        url="https://study.miigaik.ru/?groupId=2050",
        expand=True,
        on_page_started=lambda e: show_loader(e),
        on_page_ended=lambda e: show_webview(e),
        on_web_resource_error=lambda e: show_error(e)  # Ловим ошибки сети
    )

    # Функции управления состоянием с выводом логов
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
        # Если сайт не доступен или нет интернета — вы увидите это в терминале
        print(f"[ERROR] Ошибка загрузки ресурса в WebView! Детали: {e.data if hasattr(e, 'data') else e}")

    # Используем Stack, чтобы элементы не сдвигали друг друга при изменении видимости
    page.add(
        ft.Stack(
            controls=[
                web_view,
                progress_indicator
            ],
            expand=True
        )
    )
    print("[DEBUG] Элементы добавлены на страницу. Ожидание ответа от WebView...")

# Исправленный запуск приложения
if __name__ == "__main__":
    ft.run(main=main)
