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

if "rerun" not in st.session_state:
    st.session_state["rerun"] = False

# ================= HELPER FUNCTIONS =================
def send_email(to_email, subject, content):
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
    if not task["remind"] or not task["email"]:
        return
    due_dt = datetime.fromisoformat(task["due"])
    remind_before = timedelta(minutes=task["reminder_time"])
    send_time = due_dt - remind_before
    now = datetime.now(timezone.utc)
    delay = (send_time - now).total_seconds()
    if delay <= 0:
        subject = f"Reminder: {task['title']}"
        content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
        send_email(task["email"], subject, content)
    else:
        def wait_and_send():
            t.sleep(delay)
            subject = f"Reminder: {task['title']}"
            content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
            send_email(task["email"], subject, content)
        threading.Thread(target=wait_and_send, daemon=True).start()

def delete_task(task_id):
    st.session_state["tasks"] = [t for t in st.session_state["tasks"] if t["id"] != task_id]
    st.success(f"🗑 Task {task_id} deleted successfully")
    st.session_state["rerun"] = True  # set flag to rerun after loop

def update_task(task_id, updated_task):
    for i, t in enumerate(st.session_state["tasks"]):
        if t["id"] == task_id:
            st.session_state["tasks"][i] = updated_task
            st.success(f"✏️ Task {task_id} updated successfully")
            st.session_state["rerun"] = True  # set flag to rerun after loop
            break

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
            schedule_email(task)

# ================= LIST / UPDATE / DELETE TASKS =================
elif choice == "List Tasks":
    st.subheader("📋 All Tasks")
    tasks = st.session_state["tasks"]
    tasks_sorted = sorted(tasks, key=lambda x: x["due"])

    if not tasks_sorted:
        st.info("No tasks available.")
    else:
        for t in tasks_sorted:
            st.write(f"ID: {t.get('id', 'N/A')}")
            st.write(f"Title: {t.get('title', 'N/A')}")
            st.write(f"Description: {t.get('description', 'N/A')}")
            st.write(f"Email: {t.get('email', 'N/A')}")
            st.write(f"Priority: {t.get('priority', 'N/A')}")
            st.write(f"Due: {t.get('due', 'N/A')}")
            st.write(f"Reminder: {'Enabled' if t.get('remind', False) else 'Off'}")
            st.write(f"Reminder Before: {t.get('reminder_time', 0)} min")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Delete Task {t['id']}", key=f"del_{t['id']}"):
                    delete_task(t["id"])
            with col2:
                if st.button(f"Update Task {t['id']}", key=f"upd_{t['id']}"):
                    st.session_state["update_task"] = t

    # Safe rerun after loop
    if st.session_state["rerun"]:
        st.session_state["rerun"] = False
        st.experimental_rerun()

# ================= UPDATE TASK FORM (Sidebar) =================
if "update_task" in st.session_state:
    t = st.session_state.pop("update_task")
    st.sidebar.subheader(f"✏️ Update Task {t['id']}")
    t_title = st.sidebar.text_input("Task Title", value=t["title"])
    t_description = st.sidebar.text_area("Description", value=t["description"])
    t_email = st.sidebar.text_input("Email for Reminder 📩", value=t["email"])
    t_priority = st.sidebar.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(t["priority"]))
    t_due_date = st.sidebar.date_input("Due Date", value=datetime.fromisoformat(t["due"]).date())
    t_due_time = st.sidebar.time_input("Due Time", value=datetime.fromisoformat(t["due"]).time())
    t_remind = st.sidebar.checkbox("Enable Email Reminder?", value=t["remind"])
    t_reminder_minutes = st.sidebar.selectbox("Remind Me Before (minutes)", [0, 5, 10, 15, 30, 60], index=[0,5,10,15,30,60].index(t["reminder_time"]))

    if st.sidebar.button("Update Task"):
        due_dt = datetime.combine(t_due_date, t_due_time).astimezone(timezone.utc)
        updated_task = {
            "id": t["id"],
            "title": t_title,
            "description": t_description,
            "email": t_email,
            "priority": t_priority,
            "due": due_dt.isoformat(),
            "remind": t_remind,
            "reminder_time": t_reminder_minutes
        }
        update_task(t["id"], updated_task)
        schedule_email(updated_task)
        st.experimental_rerun()
