import flet as ft
from datetime import datetime
from db import get_connection


def insert_leave_application(emp_id, leave_type, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leave_applications (emp_id, leave_type, reason, status)
        VALUES (%s, %s, %s, 'pending')
    """, (emp_id, leave_type, reason))
    conn.commit()
    cursor.close()
    conn.close()


def submit_leave_application(page: ft.Page, emp_id):
    """
    Opens a dialog for the logged-in employee to submit a leave application.
    Call this from the employee portal, e.g.:
        on_click=lambda e: submit_leave_application(page, current_emp_id)
    """
    
    leave_type_dropdown = ft.Dropdown(
        label="Leave Type",
        options=[
            ft.dropdown.Option("sick", "Sick Leave"),
            ft.dropdown.Option("annual", "Annual Leave"),
            ft.dropdown.Option("unpaid", "Unpaid Leave"),
            ft.dropdown.Option("other", "Other"),
        ],
    )
    # start_date_field = ft.TextField(label="Start Date (YYYY-MM-DD)", hint_text="e.g. 2026-09-01")
    # end_date_field = ft.TextField(label="End Date (YYYY-MM-DD)", hint_text="e.g. 2026-09-05")
    reason_field = ft.TextField(label="Reason", multiline=True, min_lines=2, max_lines=4)
    error_text = ft.Text("", color=ft.Colors.RED)

    def close_dialog(e):
        dialog.open = False
        page.update()

    def clear_form():
        leave_type_dropdown.value = None
        # start_date_field.value = ""
        # end_date_field.value = ""
        reason_field.value = ""
        for f in [leave_type_dropdown, reason_field]:
            f.error_text = None
        error_text.value = ""

    def submit(e):
        errors = []

        if not leave_type_dropdown.value:
            leave_type_dropdown.error_text = "Required"
            errors.append(True)
        else:
            leave_type_dropdown.error_text = None

        # start_date = None
        # end_date = None


        if not reason_field.value:
            reason_field.error_text = "Required"
            errors.append(True)
        else:
            reason_field.error_text = None

        page.update()

        if errors:
            error_text.value = "Please fix the highlighted fields."
            page.update()
            return

        try:
            insert_leave_application(
                emp_id,
                leave_type_dropdown.value,
                reason_field.value,
            )
            dialog.open = False
            page.update()

            snack = ft.SnackBar(
                content=ft.Text("Leave application submitted successfully."),
                open=True,
            )
            page.overlay.append(snack)
            clear_form()
            page.update()

        except Exception as ex:
            error_text.value = f"Error submitting application: {ex}"
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        # bgcolor=ft.Colors.BLUE_GREY_50,
        # fgcolor=ft.Colors.BLACK,
        title=ft.Text("Submit Leave Application"),
        content=ft.Container(
            content=ft.Column(
                [
                    leave_type_dropdown,
                    # start_date_field,
                    # end_date_field,
                    reason_field,
                    error_text,
                ],
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            width=400,
            height=200,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.Button("Submit", on_click=submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()

# ft.run(submit_leave_application, emp_id)  # Example usage; replace with actual emp_id in your app