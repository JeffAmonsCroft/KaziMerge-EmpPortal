import flet as ft
import requests
from datetime import datetime, date
from zoneinfo import ZoneInfo
from db import get_connection
import geocoder


# ---------- Location helper ----------

def get_location_from_ip(page: ft.Page):
    # try:
    #     ip = page.client_ip
    #     print("DEBUG client_ip:", ip)

    #     if not ip or ip in ("127.0.0.1", "::1"):
    #         return "Local/Unknown (localhost)"

    #     resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
    #     print("DEBUG status:", resp.status_code)
    #     print("DEBUG body:", resp.text[:300])

    #     if resp.status_code != 200 or not resp.text.strip():
    #         return f"Location lookup failed (HTTP {resp.status_code})"

    #     data = resp.json()
    #     if data.get("error"):
    #         return f"Location lookup failed ({data.get('reason', 'unknown error')})"

    #     city = data.get("city", "")
    #     region = data.get("region", "")
    #     country = data.get("country_name", "")
    #     return f"{city}, {region}, {country}"

    # except requests.exceptions.RequestException as ex:
    #     return f"Location unavailable (network error: {ex})"
    # except ValueError:
    #     return "Location unavailable (invalid response from lookup service)"
    # except Exception as ex:
    #     return f"Location unavailable ({ex})"
        """
        Approximate location using the client's IP address, via geocoder.
        """
        try:
            ip = page.client_ip
            if not ip or ip in ("127.0.0.1", "::1"):
                return "Local/Unknown (localhost)"

            g = geocoder.ip(ip)

            if not g.ok:
                return f"Location lookup failed ({g.status})"

            city = g.city or ""
            state = g.state or ""
            country = g.country or ""
            return f"{city}, {state}, {country}"

        except Exception as ex:
            return f"Location unavailable ({ex})"


# ---------- Database helpers ----------

def get_today_attendance(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT attendance_id, check_in, check_out
        FROM attendance
        WHERE Emp_ID = %s AND date = %s
    """, (emp_id, date.today()))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def insert_clock_in(emp_id, check_in_time, location_in):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (Emp_ID, date, check_in, status, location_in)
        VALUES (%s, %s, %s, 'present', %s)
    """, (emp_id, date.today(), check_in_time, location_in))
    conn.commit()
    cursor.close()
    conn.close()


def update_clock_out(attendance_id, check_out_time, location_out):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE attendance
        SET check_out = %s, location_out = %s
        WHERE attendance_id = %s
    """, (check_out_time, location_out, attendance_id))
    conn.commit()
    cursor.close()
    conn.close()


# ---------- Dialog ----------

def open_attendance_dialog(page: ft.Page, emp_id):
    """
    Opens a dialog with Clock In / Clock Out buttons and status text.
    Call this from the employee portal button, e.g.:
        on_click=lambda e: open_attendance_dialog(page, emp_id)
    """

    status_text = ft.Text("", size=13)
    clock_in_btn = ft.Button("Clock In", icon=ft.Icons.LOGIN)
    clock_out_btn = ft.Button("Clock Out", icon=ft.Icons.LOGOUT)

    def close_dialog(e):
        dialog.open = False
        page.update()

    def refresh_status():
        record = get_today_attendance(emp_id)
        if not record:
            status_text.value = "Not clocked in today."
            clock_in_btn.disabled = False
            clock_out_btn.disabled = True
        elif record[1] and not record[2]:
            status_text.value = f"Clocked in at {record[1]}. Not clocked out yet."
            clock_in_btn.disabled = True
            clock_out_btn.disabled = False
        else:
            status_text.value = f"Completed today: In {record[1]} / Out {record[2]}."
            clock_in_btn.disabled = True
            clock_out_btn.disabled = True
        page.update()

    def clock_in(e):
        clock_in_btn.disabled = True
        page.update()

        location_in = get_location_from_ip(page)
        now = datetime.now(ZoneInfo("Africa/Kampala")).time().replace(microsecond=0)

        try:
            insert_clock_in(emp_id, now, location_in)
            snack = ft.SnackBar(content=ft.Text(f"Clocked in at {now} ({location_in})"), open=True)
            page.overlay.append(snack)
        except Exception as ex:
            snack = ft.SnackBar(content=ft.Text(f"Error clocking in: {ex}"), open=True)
            page.overlay.append(snack)

        refresh_status()

    def clock_out(e):
        clock_out_btn.disabled = True
        page.update()

        record = get_today_attendance(emp_id)
        if not record:
            refresh_status()
            return

        attendance_id = record[0]
        location_out = get_location_from_ip(page)
        now = datetime.now(ZoneInfo("Africa/Kampala")).time().replace(microsecond=0)

        try:
            update_clock_out(attendance_id, now, location_out)
            snack = ft.SnackBar(content=ft.Text(f"Clocked out at {now} ({location_out})"), open=True)
            page.overlay.append(snack)
        except Exception as ex:
            snack = ft.SnackBar(content=ft.Text(f"Error clocking out: {ex}"), open=True)
            page.overlay.append(snack)

        refresh_status()

    clock_in_btn.on_click = clock_in
    clock_out_btn.on_click = clock_out

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Attendance"),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row([clock_in_btn, clock_out_btn], spacing=10),
                    status_text,
                ],
                spacing=15,
                tight=True,
            ),
            width=350,
            height=150,
        ),
        actions=[
            ft.TextButton("Close", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    refresh_status()