# streamlit_app.py
import streamlit as st
from datetime import datetime, date, time, timedelta, timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import threading
import time as t

# ================= CONFIG =================
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY")
FROM_EMAIL = st.secrets.get("FROM_EMAIL")

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

menu = ["Add Task", "List Tasks"]
choice = st.sidebar.selectbox("📌 Menu", menu)

# ================= SESSION STATE =================
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

# ================= HELPER FUNCTIONS =================
def send_email(to_email, subject, content):
    """Send email via SendGrid"""
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        st.warning("⚠ SendGrid API key or sender email missing!")
        return

    if not to_email:
        st.warning("⚠ Task has no recipient email!")
        return

    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        st.success(f"📩 Email sent to {to_email}")
    except Exception as e:
        st.error(f"❌ Email failed: {e}")

def schedule_email(task):
    """Schedule email reminder using a separate thread"""
    if not task["remind"] or not task["email"]:
        return

    due_dt = datetime.fromisoformat(task["due"])
    remind_before = timedelta(minutes=task["reminder_time"])
    send_time = due_dt - remind_before
    now = datetime.now(timezone.utc)

    delay = (send_time - now).total_seconds()
    if delay <= 0:
        # Time passed or immediate email
        subject = f"Reminder: {task['title']}"
        content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
        send_email(task["email"], subject, content)
    else:
        # Schedule future email
        def wait_and_send():
            t.sleep(delay)
            subject = f"Reminder: {task['title']}"
            content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
            send_email(task["email"], subject, content)

        threading.Thread(target=wait_and_send, daemon=True).start()

# ================= ADD TASK =================
if choice == "Add Task":
    st.subheader("➕ Add New Task")

    title = st.text_input("Task Title")
    description = st.text_area("Description")
    email = st.text_input("Email for Reminder 📩")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    due_date = st.date_input("Due Date", min_value=date.today())
    due_time = st.time_input("Due Time", value=time(12,0))

    remind = st.checkbox("Enable Email Reminder?")
    reminder_minutes = st.selectbox("Remind Me Before (minutes)", [0, 5, 10, 15, 30, 60])

    if st.button("Add Task"):
        if not title or not email:
            st.warning("Please provide both Task Title and Email")
        else:
            due_dt = datetime.combine(due_date, due_time).astimezone(timezone.utc)
            task = {
                "id": len(st.session_state["tasks"]) + 1,
                "title": title,
                "description": description,
                "email": email,
                "priority": priority,
                "due": due_dt.isoformat(),
                "remind": remind,
                "reminder_time": reminder_minutes
            }
            st.session_state["tasks"].append(task)
            st.success("🎉 Task Added Successfully")

            # Schedule the email reminder
            schedule_email(task)

# ================= LIST TASKS =================
elif choice == "List Tasks":
    st.subheader("📋 All Tasks")
    tasks = st.session_state["tasks"]

    if not tasks:
        st.info("No tasks available.")
    else:
        for t in tasks:
            st.markdown(f"""
                <div style="border:1px solid #555; padding:12px; border-radius:10px; margin-bottom:10px;">
                    <b>ID:</b> {t.get('id', 'N/A')}<br>
                    <b>Title:</b> {t.get('title', 'N/A')}<br>
                    <b>Description:</b> {t.get('description', 'N/A')}<br>
                    <b>Email:</b> {t.get('email', 'N/A')}<br>
                    <b>Priority:</b> {t.get('priority', 'N/A')}<br>
                    <b>Due:</b> {t.get('due', 'N/A')}<br>
                    <b>Reminder:</b> {"Enabled" if t.get('remind', False) else "Off"}<br>
                    <b>Reminder Before:</b> {t.get('reminder_time', 0)} min
                </div>
            """, unsafe_allow_html=True)
