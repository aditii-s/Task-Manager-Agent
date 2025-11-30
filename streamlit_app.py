# streamlit_app.py
import streamlit as st
from datetime import datetime, date, time, timedelta, timezone
import sqlite3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from dateutil import parser

# ================= CONFIG =================
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY")
FROM_EMAIL = st.secrets.get("FROM_EMAIL")
DB_FILE = "tasks.db"

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

menu = ["Add Task", "List Tasks"]
choice = st.sidebar.selectbox("📌 Menu", menu)

# ================= DATABASE =================
def get_connection():
    return sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        email TEXT,
        priority TEXT,
        due TEXT,
        remind INTEGER,
        reminder_time INTEGER,
        remind_sent INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= HELPER FUNCTIONS =================
def save_task_to_db(task):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, email, priority, due, remind, reminder_time, remind_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (task["title"], task["description"], task["email"], task["priority"],
          task["due"], int(task["remind"]), task["reminder_time"], int(task.get("remind_sent", 0))))
    conn.commit()
    conn.close()

def update_task_in_db(task_id, task):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE tasks SET title=?, description=?, email=?, priority=?, due=?, remind=?, reminder_time=?, remind_sent=?
        WHERE id=?
    """, (task["title"], task["description"], task["email"], task["priority"],
          task["due"], int(task["remind"]), task["reminder_time"], int(task.get("remind_sent", 0)), task_id))
    conn.commit()
    conn.close()

def delete_task_from_db(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks ORDER BY due")
    rows = c.fetchall()
    conn.close()
    tasks = []
    for r in rows:
        tasks.append({
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "email": r[3],
            "priority": r[4],
            "due": r[5],
            "remind": bool(r[6]),
            "reminder_time": r[7],
            "remind_sent": bool(r[8])
        })
    return tasks

def send_email(to_email, subject, content):
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
    now = datetime.now(timezone.utc)
    tasks = get_all_tasks()
    for task in tasks:
        if task["remind_sent"]:
            continue
        try:
            due_dt = parser.isoparse(task["due"])
        except Exception:
            due_dt = datetime.now(timezone.utc)
        remind_before = timedelta(minutes=task["reminder_time"])
        send_time = due_dt - remind_before
        if now >= send_time and task["remind"]:
            subject = f"Reminder: {task['title']}"
            content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
            send_email(task["email"], subject, content)
            task["remind_sent"] = True
            update_task_in_db(task["id"], task)

# ================= BACKGROUND SCHEDULER =================
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_due_emails, 'interval', minutes=1)
    scheduler.start()

threading.Thread(target=start_scheduler, daemon=True).start()

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
                "reminder_time": reminder_minutes,
                "remind_sent": False
            }
            save_task_to_db(task)
            st.success("🎉 Task Added Successfully")
            st.experimental_rerun()

# ================= LIST / DELETE TASKS =================
elif choice == "List Tasks":
    st.subheader("📋 All Tasks")
    tasks = get_all_tasks()
    if not tasks:
        st.info("No tasks available.")
    else:
        for t in tasks:
            st.markdown(f"""
                ID: {t['id']}  
                Title: {t['title']}  
                Description: {t['description']}  
                Email: {t['email']}  
                Priority: {t['priority']}  
                Due: {t['due']}  
                Reminder: {"Enabled" if t['remind'] else "Off"}  
                Reminder Before: {t['reminder_time']} min  
            """)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Delete Task {t['id']}", key=f"del_{t['id']}"):
                    st.session_state["task_to_delete"] = t["id"]
            with col2:
                if st.button(f"Update Task {t['id']}", key=f"upd_{t['id']}"):
                    st.session_state["update_task"] = t

    if "task_to_delete" in st.session_state:
        delete_task_from_db(st.session_state.pop("task_to_delete"))
        st.experimental_rerun()

# ================= UPDATE TASK FORM (Sidebar) =================
if "update_task" in st.session_state:
    t = st.session_state["update_task"]
    st.sidebar.subheader(f"✏️ Update Task {t['id']}")

    try:
        due_dt = parser.isoparse(t["due"])
    except Exception:
        due_dt = datetime.now(timezone.utc)

    t_title = st.sidebar.text_input("Task Title", value=t["title"], key=f"title_{t['id']}")
    t_description = st.sidebar.text_area("Description", value=t["description"], key=f"description_{t['id']}")
    t_email = st.sidebar.text_input("Email for Reminder 📩", value=t["email"], key=f"email_{t['id']}")
    t_priority = st.sidebar.selectbox(
        "Priority", ["Low", "Medium", "High"], 
        index=["Low", "Medium", "High"].index(t["priority"]),
        key=f"priority_{t['id']}"
    )
    t_due_date = st.sidebar.date_input("Due Date", value=due_dt.date(), key=f"duedate_{t['id']}")
    t_due_time = st.sidebar.time_input("Due Time", value=due_dt.time(), key=f"duetime_{t['id']}")
    t_remind = st.sidebar.checkbox("Enable Email Reminder?", value=t["remind"], key=f"remind_{t['id']}")
    t_reminder_minutes = st.sidebar.selectbox(
        "Remind Me Before (minutes)", 
        [0, 5, 10, 15, 30, 60], 
        index=[0,5,10,15,30,60].index(t["reminder_time"]), 
        key=f"remindtime_{t['id']}"
    )

    if st.sidebar.button("Update Task", key=f"updatebtn_{t['id']}"):
        due_dt_combined = datetime.combine(t_due_date, t_due_time).astimezone(timezone.utc)
        updated_task = {
            "id": t["id"],
            "title": t_title,
            "description": t_description,
            "email": t_email,
            "priority": t_priority,
            "due": due_dt_combined.isoformat(),
            "remind": t_remind,
            "reminder_time": t_reminder_minutes,
            "remind_sent": t["remind_sent"]
        }
        update_task_in_db(t["id"], updated_task)
        st.success(f"Task {t['id']} updated successfully!")
        st.session_state.pop("update_task")
        st.experimental_rerun()
