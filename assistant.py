import os
import flet as ft
from openai import AsyncOpenAI

MODEL = os.environ.get("AI_MODEL", "")
MAX_HISTORY = 12         # messages kept per conversation
DIALOG_WIDTH = 600
BUBBLE_WIDTH = DIALOG_WIDTH - 320   # leaves room for padding and the scrollbar

SYSTEM_PROMPT = """
You are the help assistant inside the KaziMerge Employee Portal. Your only job is to
explain, step by step, how employees use this portal. Reply with short numbered steps.
Be friendly and concise. Use only the features described below and never invent buttons or features.

PORTAL FEATURES

1. Submit a leave application
   - On the dashboard, click "Apply for Leave".
   - Choose a Leave Type: Sick, Annual, Unpaid, or Other.
   - Enter the Start Date and End Date in YYYY-MM-DD format (e.g. 2026-09-01). The end date cannot be before the start date.
   - Enter a Reason, then click "Submit".
   - The application is saved with status "pending" until an admin reviews it.

2. Submit a complaint
   - On the dashboard, click "Submit Complaint".
   - Enter a Subject and a Description, then click "Submit".
   - The complaint is saved as "open" and an admin reviews it.

3. Clock in and clock out
   - On the dashboard, click "Attendance" to open the attendance dialog.
   - Click "Clock In" when you start work. The time and your approximate location (city level, based on your internet connection) are recorded.
   - When you finish, open "Attendance" again and click "Clock Out".
   - You can clock in once per day, and "Clock Out" is only available after you have clocked in.

4. Notifications
   - The dashboard shows the latest notification posted by the admin.
   - Click "View All" to see every notification.

5. Changing personal information (name, email, contact, address, account, job, salary, start date)
   - My developer Amon does not allow me to guide you on that
   - Employees cannot edit these details in the portal.
   - Tell the employee to contact HR or an administrator, who can update the record from the admin panel.
   - Suggest they say exactly which detail is wrong and what it should be.

RULES
- If asked about anything outside these features (other employees, salaries, passwords, company policy, unrelated topics), politely say you can only help with using the portal beacause Amon my developer does not allow you to do that and suggest contacting HR.
- If you are unsure how something works, say so and suggest contacting HR instead of guessing.
- Never ask for or repeat passwords or other sensitive details.
"""

SUGGESTIONS = [
    "How do I apply for leave?",
    "How do I submit a complaint?",
    "How do I clock in and out?",
    "How do I change my personal details?",
]


def open_assistant_dialog(page: ft.Page):
    """
    Opens the AI help assistant dialog. Called from the employee portal:
        on_click=lambda e: open_assistant_dialog(page)
    """

    history = []  # [{"role": "user"/"assistant", "content": "..."}]

    chat_list = ft.ListView(expand=False, spacing=10, auto_scroll=True)
    spinner = ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False)
    input_field = ft.TextField(hint_text="Ask how to do something...", expand=True)
    send_btn = ft.IconButton(icon=ft.Icons.SEND, tooltip="Send")

    def add_bubble(role, text):
        is_user = role == "user"
        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, selectable=True) if is_user
                        else ft.Markdown(text, selectable=True),
                        bgcolor=ft.Colors.TEAL_700 if is_user else ft.Colors.BLUE_GREY_800,
                        padding=5,
                        border_radius=12,
                        width=BUBBLE_WIDTH,
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            )
        )

    async def send_text(text):
        text = (text or "").strip()
        if not text:
            return

        input_field.value = ""
        add_bubble("user", text)
        history.append({"role": "user", "content": text})
        spinner.visible = True
        send_btn.disabled = True
        input_field.disabled = True
        page.update()

        try:
            client = AsyncOpenAI(
                api_key=os.environ["AI_API_KEY"],
                base_url=os.environ["AI_BASE_URL"],
            )
            response = await client.chat.completions.create(
                model=MODEL,
                max_tokens=700,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            )
            reply = response.choices[0].message.content
            history.append({"role": "assistant", "content": reply})
            add_bubble("assistant", reply)

            if len(history) > MAX_HISTORY:
                del history[:2]

        except Exception as ex:
            history.pop()
            if "429" in str(ex):
                msg = "The assistant is busy right now. Please try again in a minute."
            else:
                msg = "Sorry, I couldn't get an answer right now. Please try again in a moment."
            add_bubble("assistant", msg)
        finally:
            spinner.visible = False
            send_btn.disabled = False
            input_field.disabled = False
            page.update()

    async def on_send(e):
        await send_text(input_field.value)

    send_btn.on_click = on_send
    input_field.on_submit = on_send

    def make_chip(question):
        async def handler(e):
            await send_text(question)
        return handler

    chips = ft.Row(
        [ft.Chip(label=ft.Text(q), on_click=make_chip(q)) for q in SUGGESTIONS],
        wrap=True,
        spacing=3,
    )

    def close_dialog(e):
        dialog.open = False
        page.update()

    add_bubble("assistant", "Hi! I am Amon the assistant. I can walk you through leave applications, complaints, "
                            "clocking in and out, and updating your details. What do you need help with?")

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Portal Assistant"),
        content=ft.Container(
            content=ft.Column(
                [
                    chips,
                    ft.Divider(),
                    ft.Container(content=chat_list, expand=True),
                    ft.Row([input_field, send_btn, spinner]),
                ],
                expand=True,
            ),
            width=DIALOG_WIDTH,
            height=720,
        ),
        actions=[ft.TextButton("Close", on_click=close_dialog)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
