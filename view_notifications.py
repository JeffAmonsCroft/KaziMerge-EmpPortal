import flet as ft
from db import get_connection


def fetch_all_notifications():
    """Fetch all notifications."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, message, posted_on
        FROM notifications
        ORDER BY posted_on DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def view_notifications(page: ft.Page):
    """
    Opens a dialog showing all posted notifications.
    Call this from the employee portal, e.g.:
        on_click=lambda e: view_notifications(page)
    """
    def close_dialog(e):
        dialog.open = False
        page.update()

    try:
        notifications = fetch_all_notifications()
        error_message = None
    except Exception as ex:
        notifications = []
        error_message = str(ex)

    if error_message:
        body = ft.Text(f"Error loading notifications: {error_message}", color=ft.Colors.RED)
    elif not notifications:
        body = ft.Text("No notifications yet.", italic=True)
    else:
        items = []
        for title, message, posted_on in notifications:
            items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(message),
                            ft.Text(str(posted_on), size=11, color=ft.Colors.GREY),
                        ],
                        spacing=4,
                    ),
                    padding=12,
                    # border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    # margin=ft.margin.only(bottom=8),
                )
            )
        body = ft.Column(items, scroll=ft.ScrollMode.AUTO)

    dialog = ft.AlertDialog(
        modal=True,
        # bgcolor=ft.Colors.BLUE_GREY_50,
        # fgcolor=ft.Colors.BLACK,
        title=ft.Text("Notifications"),
        content=ft.Container(
            content=body,
            width=450,
            height=400,
        ),
        actions=[
            ft.TextButton("Close", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()