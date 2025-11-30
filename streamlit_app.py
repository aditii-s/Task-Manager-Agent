# streamlit_app.py
import streamlit as st
from datetime import datetime, date, time, timedelta, timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
import os

# ================= CONFIG =================
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY")
FROM_EMAIL = st.secrets.get("FROM_EMAIL")
TASK_FILE = "tasks.json"

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

menu = ["Add Task", "List Tasks"]
choice = st.sidebar.selectbox("📌 Menu", menu)

# ================= SESSION STATE =================
if "tasks" not in st.session_state:
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            st.session_state["tasks"] = json.load(f)
    else:
        st.session_state["tasks"] = []

# ================= HELPER FUNCTIONS =================
def save_tasks():
    with open(TASK_FILE, "w") as f:
        json.dump(st.session_state["tasks"], f, indent=4)

def send_email(to_email, subject, content):
    """Send email via SendGrid"""
    if not SENDGRID_API_KEY or not FROM_EMAIL or not to_email:
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
    except Exception as e:
        st.warning(f"Email failed: {e}")

def process_due_emails():
    """Send email reminders for due tasks"""
    now = datetime.now(timezone.utc)
    for task in st.session_state["tasks"]:
        if task.get("remind_sent"):
            continue  # Skip if email already sent
        due_dt = datetime.fromisoformat(task["due"])
        remind_before = timedelta(minutes=task["reminder_time"])
        send_time = due_dt - remind_before
        if now >= send_time and task["remind"]:
            subject = f"Reminder: {task['title']}"
            content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
            send_email(task["email"], subject, content)
            task["remind_sent"] = True
    save_tasks()

def add_task(task):
    task["id"] = max([t["id"] for t in st.session_state["tasks"]], default=0) + 1
    task["remind_sent"] = False
    st.session_state["tasks"].append(task)
    save_tasks()

def update_task(task_id, updated_task):
    for i, t in enumerate(st.session_state["tasks"]):
        if t["id"] == task_id:
            updated_task["remind_sent"] = t.get("remind_sent", False)
            st.session_state["tasks"][i] = updated_task
            save_tasks()
            break

def delete_task(task_id):
    st.session_state["tasks"] = [t for t in st.session_state["tasks"] if t["id"] != task_id]
    save_tasks()

# ================= EMAIL REMINDERS =================
process_due_emails()

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
                "title": title,
                "description": description,
                "email": email,
                "priority": priority,
                "due": due_dt.isoformat(),
                "remind": remind,
                "reminder_time": reminder_minutes
            }
            add_task(task)
            st.success("🎉 Task Added Successfully")

# ================= LIST / UPDATE / DELETE TASKS =================
elif choice == "List Tasks":
    st.subheader("📋 All Tasks")
    tasks = sorted(st.session_state["tasks"], key=lambda x: x["due"])
    if not tasks:
        st.info("No tasks available.")
    else:
        for t in tasks:
            st.markdown(f"""
                ID: {t.get('id', 'N/A')}  
                Title: {t.get('title', 'N/A')}  
                Description: {t.get('description', 'N/A')}  
                Email: {t.get('email', 'N/A')}  
                Priority: {t.get('priority', 'N/A')}  
                Due: {t.get('due', 'N/A')}  
                Reminder: {"Enabled" if t.get('remind', False) else "Off"}  
                Reminder Before: {t.get('reminder_time', 0)} min  
            """)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Delete Task {t['id']}", key=f"del_{t['id']}"):
                    delete_task(t["id"])
                    st.experimental_rerun()
            with col2:
                if st.button(f"Update Task {t['id']}", key=f"upd_{t['id']}"):
                    st.session_state["update_task"] = t
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
        process_due_emails()
        st.experimental_rerun()

