import flet as ft
import os
from employee_login import build_login
from employee_dashboard import build_dashboard


def main(page: ft.Page):
    page.title = "EMS"
    page.window.width = 650
    page.window.height = 800
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0

    session = {}  # holds logged-in user's data in memory

    def show_login():
        page.controls.clear()
        page.add(build_login(page, session, on_login_success=show_dashboard))
        page.update()

    def show_dashboard():
        page.controls.clear()
        page.add(build_dashboard(page, session, on_logout=show_login))
        page.update()

    show_login()  # start on the login screen


# ft.app(
#     target=main,
#     view=ft.AppView.WEB_BROWSER,
#     port=int(os.environ.get("PORT", 8000)),
#     host="0.0.0.0"
# )
ft.run(main)
