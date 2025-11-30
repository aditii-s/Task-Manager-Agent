# streamlit_app.py
import streamlit as st
from datetime import datetime, date, time, timedelta, timezone
import sqlite3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ================= CONFIG =================
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY")
FROM_EMAIL = st.secrets.get("FROM_EMAIL")
DB_FILE = "tasks.db"

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

# ================= DATABASE FUNCTIONS =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            email TEXT,
            priority TEXT,
            due TEXT,
            remind INTEGER,
            reminder_time INTEGER,
            remind_sent INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_task_db(task):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure email column exists
    try:
        c.execute("ALTER TABLE tasks ADD COLUMN email TEXT")
        conn.commit()
    except:
        pass
    c.execute("""
        INSERT INTO tasks (title, description, email, priority, due, remind, reminder_time, remind_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (task["title"], task["description"], task["email"], task["priority"],
          task["due"], int(task["remind"]), task["reminder_time"], int(task.get("remind_sent", 0))))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, title, description, email, priority, due, remind, reminder_time, remind_sent FROM tasks
    """)
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

def update_task_db(task_id, updated_task):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE tasks
        SET title=?, description=?, email=?, priority=?, due=?, remind=?, reminder_time=?, remind_sent=?
        WHERE id=?
    """, (updated_task["title"], updated_task["description"], updated_task["email"], updated_task["priority"],
          updated_task["due"], int(updated_task["remind"]), updated_task["reminder_time"], int(updated_task.get("remind_sent", 0)), task_id))
    conn.commit()
    conn.close()

def delete_task_db(task_id):
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
        if task.get("remind_sent"):
            continue
        due_dt = datetime.fromisoformat(task["due"])
        remind_before = timedelta(minutes=task["reminder_time"])
        send_time = due_dt - remind_before
        if now >= send_time and task["remind"]:
            subject = f"Reminder: {task['title']}"
            content = f"<b>Task:</b> {task['title']}<br><b>Description:</b> {task['description']}<br><b>Due:</b> {task['due']}"
            send_email(task["email"], subject, content)
            task["remind_sent"] = True
            update_task_db(task["id"], task)

# ================= INITIALIZE DB =================
init_db()
process_due_emails()

# ================= ADD TASK =================
st.subheader("➕ Add New Task")
with st.form(key="add_task_form"):
    title = st.text_input("Task Title")
    description = st.text_area("Description")
    email = st.text_input("Email for Reminder 📩")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date", min_value=date.today())
    due_time = st.time_input("Due Time", value=time(12,0))
    remind = st.checkbox("Enable Email Reminder?")
    reminder_minutes = st.selectbox("Remind Me Before (minutes)", [0, 5, 10, 15, 30, 60])
    submitted = st.form_submit_button("Add Task")
    if submitted:
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
            add_task_db(task)
            st.success("🎉 Task Added Successfully")
            st.experimental_rerun()

# ================= LIST / UPDATE / DELETE TASKS =================
st.subheader("📋 All Tasks")
tasks = sorted(get_all_tasks(), key=lambda x: x["due"])
if not tasks:
    st.info("No tasks available.")
else:
    for t in tasks:
        st.markdown("---")
        st.markdown(f"""
            **ID:** {t['id']}  
            **Title:** {t['title']}  
            **Description:** {t['description']}  
            **Email:** {t['email']}  
            **Priority:** {t['priority']}  
            **Due:** {t['due']}  
            **Reminder:** {"Enabled" if t['remind'] else "Off"}  
            **Reminder Before:** {t['reminder_time']} min  
        """)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Delete Task {t['id']}", key=f"del_{t['id']}"):
                delete_task_db(t["id"])
                st.experimental_rerun()
        with col2:
            if st.button(f"Update Task {t['id']}", key=f"upd_{t['id']}"):
                st.session_state["update_task"] = t
                st.experimental_rerun()

# ================= UPDATE TASK FORM =================
if "update_task" in st.session_state:
    t = st.session_state.pop("update_task")
    st.subheader(f"✏️ Update Task {t['id']}")
    with st.form(key=f"update_form_{t['id']}"):
        t_title = st.text_input("Task Title", value=t["title"])
        t_description = st.text_area("Description", value=t["description"])
        t_email = st.text_input("Email for Reminder 📩", value=t["email"])
        t_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(t["priority"]))
        t_due_date = st.date_input("Due Date", value=datetime.fromisoformat(t["due"]).date())
        t_due_time = st.time_input("Due Time", value=datetime.fromisoformat(t["due"]).time())
        t_remind = st.checkbox("Enable Email Reminder?", value=t["remind"])
        t_reminder_minutes = st.selectbox("Remind Me Before (minutes)", [0,5,10,15,30,60], index=[0,5,10,15,30,60].index(t["reminder_time"]))
        updated = st.form_submit_button("Update Task")
        if updated:
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
                "remind_sent": t.get("remind_sent", False)
            }
            update_task_db(t["id"], updated_task)
            process_due_emails()
            st.success("✅ Task Updated Successfully")
            st.experimental_rerun()
