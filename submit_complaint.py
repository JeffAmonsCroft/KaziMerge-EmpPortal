import flet as ft
from db import get_connection


def insert_complaint(emp_id, subject, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (emp_id, subject, description, status)
        VALUES (%s, %s, %s, 'open')
    """, (emp_id, subject, description))
    conn.commit()
    cursor.close()
    conn.close()


def submit_complaint(page: ft.Page, emp_id):
    """
    Opens a dialog for the logged-in employee to submit a complaint.
    Call this from the employee portal, e.g.:
        on_click=lambda e: submit_complaint(page, current_emp_id)
    """

    subject_field = ft.TextField(label="Subject")
    description_field = ft.TextField(label="Description", multiline=True, min_lines=3, max_lines=6)
    error_text = ft.Text("", color=ft.Colors.RED)

    def close_dialog(e):
        dialog.open = False
        page.update()

    def clear_form():
        subject_field.value = ""
        description_field.value = ""
        subject_field.error_text = None
        description_field.error_text = None
        error_text.value = ""

    def submit(e):
        errors = []

        if not subject_field.value:
            subject_field.error_text = "Required"
            errors.append(True)
        else:
            subject_field.error_text = None

        if not description_field.value:
            description_field.error_text = "Required"
            errors.append(True)
        else:
            description_field.error_text = None

        page.update()

        if errors:
            error_text.value = "Please fix the highlighted fields."
            page.update()
            return

        try:
            insert_complaint(emp_id, subject_field.value, description_field.value)
            dialog.open = False
            page.update()

            snack = ft.SnackBar(
                content=ft.Text("Complaint submitted successfully."),
                open=True,
            )
            page.overlay.append(snack)
            clear_form()
            page.update()

        except Exception as ex:
            error_text.value = f"Error submitting complaint: {ex}"
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        # bgcolor=ft.Colors.BLUE_GREY_50,
        # fgcolor=ft.Colors.BLACK,
        title=ft.Text("Submit Complaint"),
        content=ft.Container(
            content=ft.Column(
                [subject_field, description_field, error_text],
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