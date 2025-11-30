# streamlit_app.py
import streamlit as st
import sqlite3
from datetime import datetime, date, time, timedelta, timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# ================= CONFIG =================
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY")
FROM_EMAIL = st.secrets.get("FROM_EMAIL")
DB_FILE = "tasks.db"

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

menu = ["Add Task", "List Tasks"]
choice = st.sidebar.selectbox("📌 Menu", menu)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            email TEXT NOT NULL,
            priority TEXT,
            due TEXT,
            remind INTEGER,
            reminder_time INTEGER,
            remind_sent INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_task_to_db(task):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, email, priority, due, remind, reminder_time, remind_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task["title"],
        task["description"],
        task["email"],
        task["priority"],
        task["due"],
        int(task["remind"]),
        task["reminder_time"],
        int(task.get("remind_sent", 0))
    ))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, description, email, priority, due, remind, reminder_time, remind_sent FROM tasks")
    rows = c.fetchall()
    conn.close()
    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "email": row[3],
            "priority": row[4],
            "due": row[5],
            "remind": bool(row[6]),
            "reminder_time": row[7],
            "remind_sent": bool(row[8])
        })
    return tasks

def update_task_in_db(task_id, updated_task):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE tasks SET title=?, description=?, email=?, priority=?, due=?, remind=?, reminder_time=?, remind_sent=?
        WHERE id=?
    """, (
        updated_task["title"],
        updated_task["description"],
        updated_task["email"],
        updated_task["priority"],
        updated_task["due"],
        int(updated_task["remind"]),
        updated_task["reminder_time"],
        int(updated_task.get("remind_sent", 0)),
        task_id
    ))
    conn.commit()
    conn.close()

def delete_task_from_db(task_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

# ================= EMAIL =================
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
        due_dt = datetime.fromisoformat(task["due"])
        remind_before = timedelta(minutes=task["reminder_time"])
        send_time = due_dt - remind_before
        if now >= send_time and task["remind"]:
            subject = f"Reminder: {task['title']}"
            content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
            send_email(task["email"], subject, content)
            task["remind_sent"] = True
            update_task_in_db(task["id"], task)

# ================= INIT =================
init_db()
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
    reminder_minutes = st.selectbox("Remind Me Before (minutes)", [0,5,10,15,30,60])

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
            save_task_to_db(task)
            st.success("🎉 Task Added Successfully")
            st.experimental_rerun()

# ================= LIST / UPDATE / DELETE =================
elif choice == "List Tasks":
    st.subheader("📋 All Tasks")
    tasks = sorted(get_all_tasks(), key=lambda x: x["due"])
    if not tasks:
        st.info("No tasks available.")
    else:
        for t in tasks:
            st.markdown(f"""
                **ID:** {t['id']}  
                **Title:** {t['title']}  
                **Description:** {t['description']}  
                **Email:** {t['email']}  
                **Priority:** {t['priority']}  
                **Due:** {t['due']}  
                **Reminder:** {"Enabled" if t['remind'] else "Off"}  
                **Remind Before:** {t['reminder_time']} min
            """)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Delete Task {t['id']}", key=f"del_{t['id']}"):
                    delete_task_from_db(t["id"])
                    st.experimental_rerun()
            with col2:
                if st.button(f"Update Task {t['id']}", key=f"upd_{t['id']}"):
                    st.session_state["update_task"] = t
                    st.experimental_rerun()

# ================= UPDATE TASK FORM =================
if "update_task" in st.session_state:
    t = st.session_state.pop("update_task")
    st.sidebar.subheader(f"✏️ Update Task {t['id']}")
    t_title = st.sidebar.text_input("Task Title", value=t["title"], key=f"title_{t['id']}")
    t_description = st.sidebar.text_area("Description", value=t["description"], key=f"desc_{t['id']}")
    t_email = st.sidebar.text_input("Email for Reminder 📩", value=t["email"], key=f"email_{t['id']}")
    t_priority = st.sidebar.selectbox("Priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(t["priority"]), key=f"priority_{t['id']}")
    t_due_date = st.sidebar.date_input("Due Date", value=datetime.fromisoformat(t["due"]).date(), key=f"due_date_{t['id']}")
    t_due_time = st.sidebar.time_input("Due Time", value=datetime.fromisoformat(t["due"]).time(), key=f"due_time_{t['id']}")
    t_remind = st.sidebar.checkbox("Enable Email Reminder?", value=t["remind"], key=f"remind_{t['id']}")
    t_reminder_minutes = st.sidebar.selectbox("Remind Me Before (minutes)", [0,5,10,15,30,60],
                                              index=[0,5,10,15,30,60].index(t["reminder_time"]), key=f"remindmin_{t['id']}")

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
            "reminder_time": t_reminder_minutes,
            "remind_sent": t["remind_sent"]
        }
        update_task_in_db(t["id"], updated_task)
        st.success("✅ Task Updated Successfully")
        st.experimental_rerun()
