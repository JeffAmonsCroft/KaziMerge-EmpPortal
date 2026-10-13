import flet as ft
# from employee_dashboard import build_dashboard
from db import authenticate_employee


# global login_click, login_button

def build_login(page: ft.Page, session: dict, on_login_success):
    global login_click
    page.title = "EMS - Login"
    page.window.width = 420
    page.window.height = 750
    # page.window.center()
    page.bgcolor = ft.Colors.WHITE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0




    # --- Form fields ---
    email_field = ft.TextField(
        label="Email",
        hint_text="you@company.com",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=8,
        border_color=ft.Colors.GREY_400,
        focused_border_color=ft.Colors.TEAL_600,
        cursor_color=ft.Colors.TEAL_600,
        color=ft.Colors.BLUE_GREY_900,
        width=320,
        )

    emp_id_field = ft.TextField(
            label="Employee ID",
            hint_text="EMP-XXX",
            prefix_icon=ft.Icons.BADGE_OUTLINED,
            border_radius=8,
            border_color=ft.Colors.GREY_400,
            focused_border_color=ft.Colors.TEAL_600,
            cursor_color=ft.Colors.TEAL_600,
            color=ft.Colors.BLUE_GREY_900,
            width=320,
        )

    error_text = ft.Text(
            "",
            color=ft.Colors.RED_400,
            size=13,
            visible=False,
        )



    # admin = ["amonsekate@gmail.com"]
    
    # --- Event handler ---
    def login_click(e):
            if not email_field.value or not emp_id_field.value:
                error_text.value = "Please fill in both fields."
                login_button.disabled = False
                login_button.content = ft.Text("Log In")
                error_text.visible = True
                page.update()
                return

                # Show a loading state while querying
            login_button.disabled = True
            login_button.content = ft.Row(
                [ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.WHITE), ft.Text("Checking...")],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            )
            page.update()

            employee = authenticate_employee(email_field.value.strip(), emp_id_field.value)
            # print("DEBUG login result:", employee)

            if employee is None:
                error_text.value = "Invalid email or employee ID."
                login_button.disabled = False
                login_button.content = ft.Text("Log In")
                error_text.visible = True
                page.update()
                return
            # TODO: replace with real auth check (DB/API lookup)
            # session["email"] = email_field.value
            # session["emp_id"] = emp_id_field.value
            

            # build_dashboard(page, session, on_logout=on_login_success)
            session["employee"] = employee
            # page.session.get("emp_id")
            on_login_success()  # tells main.py to switch to the dashboard
    
            # error_text.visible = False
            # page.update()
            
    login_button = ft.Button(
        "Log In",
        icon=ft.Icons.LOGIN,
        bgcolor=ft.Colors.TEAL_600,
        color=ft.Colors.WHITE,
        width=320,
        height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=login_click,
    )
    
    return ft.Column([      
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.BUSINESS_CENTER, size=48, color=ft.Colors.TEAL_600),
                                        ft.Text("EMS", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                                        ft.Text("Employee Management System", size=13, color=ft.Colors.GREY_600),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=5,
                                ),
                                bgcolor=ft.Colors.CYAN_ACCENT_100,
                                # padding=ft.padding.symmetric(vertical=40),
            
                                width=420,
                                # alignment=ft.alignment.cen,
                            ),
            
                            ft.Container(height=30),
            
                            # Form section
                            ft.Text("Welcome back", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                            ft.Text("Sign in to continue", size=14, color=ft.Colors.GREY_600),
            
                            ft.Container(height=20),
            
                            email_field,
                            ft.Container(height=15),
                            emp_id_field,
                            ft.Container(height=10),
            
                            error_text,
            
                            ft.Container(height=15),
                            
                            login_button,
            
                            ft.Container(height=10),
            
                            ft.TextButton(
                                "Forgot your Employee ID? Contact HR.",
                                style=ft.ButtonStyle(color=ft.Colors.TEAL_600),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        )

             
    
    
# ft.run(build_login)