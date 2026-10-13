import flet as ft
# import MySQLdb
from db import submit_complaint
from db import get_connection
from submit_leave_application import submit_leave_application
from submit_complaint import submit_complaint
from view_notifications import view_notifications
from attendance import open_attendance_dialog
from assistant import open_assistant_dialog




def fetch_latest_notification():
    """Fetch only the most recent notification."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, message, posted_on
        FROM notifications
        ORDER BY posted_on DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row



def view_recent_notifications():
    try:
        latest = fetch_latest_notification()
        error_message = None
    except Exception as ex:
        latest = None
        error_message = str(ex)

    if error_message:
        latest_content = ft.Text(f"Error loading notification: {error_message}", color=ft.Colors.RED)
    elif not latest:
        latest_content = ft.Text("No notifications yet.", italic=True, color=ft.Colors.GREY)
    else:
        title, message, posted_on = latest
        latest_content = ft.Column(
            [
                ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                ft.Text(message, size=13),
                ft.Text(str(posted_on), size=11, color=ft.Colors.GREY),
            ],
            spacing=4,
        )
        return latest_content




def open_complaint_dialog(page: ft.Page, session: dict):
    AMBER = ft.Colors.AMBER_600
    ERROR_RED = ft.Colors.RED_400

    logged_in_email = session.get("employee", {}).get("Email", "")

    email_field = ft.TextField(
        label="Employee Email",
        value=logged_in_email,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=8,
        width=320,
    )

    complaint_field = ft.TextField(
        label="Complaint",
        hint_text="Describe your complaint here...",
        multiline=True,
        min_lines=4,
        max_lines=6,
        border_radius=8,
        width=320,
    )

    status_text = ft.Text("", color=ERROR_RED, size=13, visible=False)

    def close_dialog(e):
        page.pop_dialog()

    def submit_click(e):
        if not email_field.value or not complaint_field.value:
            status_text.value = "Please fill in both fields."
            status_text.visible = True
            page.update()
            return

        success = submit_complaint(email_field.value.strip(), complaint_field.value.strip())

        if success:
            page.pop_dialog()
            snack = ft.SnackBar(
                content=ft.Text("Complaint submitted successfully."),
                bgcolor=ft.Colors.GREEN_600,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        else:
            status_text.value = "Something went wrong. Please try again."
            status_text.visible = True
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Write a Complaint", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [email_field, complaint_field, status_text],
            tight=True,
            spacing=15,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.Button(
                "Submit",
                icon=ft.Icons.SEND,
                bgcolor=AMBER,
                color=ft.Colors.WHITE,
                on_click=submit_click,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(dialog)





def build_dashboard(page: ft.Page, session: dict, on_logout):
    content = view_recent_notifications()
    page.title = "EMS - Employee Portal"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 650
    page.window.height = 800
    page.padding = 0
    page.scroll = None
    # page.scroll = ft.ScrollMode.AUTO
    # await page.window.center()
    # page.scroll = "adaptive"

    employee = session.get("employee", {})
    # print("DEBUG employee data:", employee)
    # emp_email = session.get("email", "Unknown")
    # emp_id = session.get("emp_id", "Unknown")
    emp_id = employee.get('Emp_ID')

    def log_out_click(e):
        session.clear()
        on_logout()  # tells main.py to switch back to login


    header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("EMS Portal", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.IconButton(
                        tooltip="Log Out",
                        icon=ft.Icons.LOGOUT,
                        icon_color = ft.Colors.RED,
                        # bgcolor=ft.Colors.RED,
                        # color=ft.Colors.WHITE,
                        on_click=log_out_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLUE_900,
            padding=10,
        )
    scrollable_content = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Welcome, {employee.get('Name', 'Employee').upper()}!", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(height=10),
                        ft.Row([ft.Text("Employee Email: ", color=ft.Colors.WHITE), ft.Text(f"{employee.get('Email', 'Email')}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)]),
                        ft.Row([ft.Text("Employee ID: ", color=ft.Colors.WHITE), ft.Text(f"{employee.get('Emp_ID', 'ID')}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)]),
                        ft.Row([ft.Text("Category: ", color=ft.Colors.WHITE), ft.Text(f"{employee.get('Job', 'Job')}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)]),
                        ft.Row([ft.Text("Address: ", color=ft.Colors.WHITE), ft.Text(f"{employee.get('Address', 'Address')}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)]),
                    ],
                    spacing=8,
                    ),
                    bgcolor=ft.Colors.TEAL_700,
                    border_radius=10,
                    padding=20,
                ),

        # --- Announcements card ---
            ft.Container(
                content=ft.Column(
                        [   
                            ft.Row([
                                ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.WHITE),
                                ft.Text("Notifications", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ]),
                            ft.Container(height=10),
                            ft.Container(
                                content=content
                            ),
                            
                            ft.Row([ft.Button("View All", on_click=lambda e: view_notifications(page),)])
                        ],
                    ),
                    bgcolor=ft.Colors.TEAL_700,
                    border_radius=10,
                    padding=20,
                ),

    # --- Complaints card ---
            ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.REPORT_PROBLEM, color=ft.Colors.WHITE),
                                    ft.Text("Complaints", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ]
                            ),
                            ft.Container(height=15),
                            ft.Button(
                                "Write Complaint",
                                icon=ft.Icons.FEEDBACK,
                                bgcolor=ft.Colors.ORANGE_600,
                                color=ft.Colors.WHITE,
                                width=200,
                                on_click=lambda e: submit_complaint(page, emp_id),
                            ),
                        ],
                    ),
                    bgcolor=ft.Colors.TEAL_700,
                    border_radius=10,
                    padding=20,
                ),
#attendence card
            ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.EVENT_AVAILABLE, color=ft.Colors.WHITE),
                                    ft.Text("Attendance", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ]
                            ),
                            ft.Container(height=15),
                            ft.Row(
                                [   
                                    # ft.ElevatedButton("Attendance", on_click=lambda e: build_attendance_section(page, emp_id)),
                                    ft.Button("Check In/Out", on_click=lambda e: open_attendance_dialog(page, emp_id), icon=ft.Icons.ACCESS_TIME, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                                    
                                    # ft.Button(
                                    #     "Clock In",
                                    #     icon=ft.Icons.ACCESS_TIME_FILLED,
                                    #     bgcolor=ft.Colors.GREEN_600,
                                    #     color=ft.Colors.WHITE,
                                    # ),
                                    # ft.Button(
                                    #         "Clock Out",
                                    #         icon=ft.Icons.TIMER_OFF,
                                    #         bgcolor=ft.Colors.DEEP_ORANGE_400,
                                    #         color=ft.Colors.WHITE,
                                    #     ),
                                ],
                                spacing=10,
                            ),
                        ],
                    ),
                    bgcolor=ft.Colors.TEAL_700,
                    border_radius=10,
                    padding=20,
                    # margin=ft.margin.symmetric(horizontal=15, vertical=10),
                ),

        # --- Leaves card  ---
            ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.WORK_OFF, color=ft.Colors.WHITE),
                                    ft.Text("Leaves", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ]
                            ),
                            ft.Container(height=15),
                            ft.Button(
                                "Apply for Leave",
                                icon=ft.Icons.EDIT_CALENDAR,
                                bgcolor=ft.Colors.ORANGE_400,
                                color=ft.Colors.WHITE,
                                width=200,
                                on_click=lambda e: submit_leave_application(page, emp_id),
                            ),
                        ],
                    ),
                    bgcolor=ft.Colors.TEAL_700,
                    border_radius=10,
                    padding=20,
                    # margin=ft.margin.symmetric(horizontal=15, vertical=10),
                ),
                # --- AI card  ---
                ft.Container(
                            content=ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.SUPPORT_AGENT, color=ft.Colors.WHITE),
                                                    ft.Text("AI Assistant", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                                ]
                                            ),
                                            ft.Container(height=15),
                                            ft.Button(
                                                "Amon's AI Assistant",
                                                icon=ft.Icons.SUPPORT_AGENT,
                                                bgcolor=ft.Colors.BLUE_400,
                                                color=ft.Colors.WHITE,
                                                width=200,
                                                on_click=lambda e: open_assistant_dialog(page),
                )
                                        ],
                                    ),
                                    bgcolor=ft.Colors.TEAL_700,
                                    border_radius=10,
                                    padding=20,
                                    # margin=ft.margin.symmetric(horizontal=15, vertical=10),
                                ),
        ],
        scroll=ft.ScrollMode.AUTO,   # <-- this Column scrolls, not the page
        expand=True,
        padding=20,
        spacing=10
    )

    return ft.Column(
                [
                    header, 
                    # welcome_card, 
                    # announcements_card, 
                    # complaints_card, 
                    # attendance_card, 
                    # leaves_card,
                    scrollable_content  
                ],
                expand=True,
                spacing=10,
                
            )
            

# ft.run(build_dashboard,)
