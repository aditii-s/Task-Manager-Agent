import streamlit as st
import sqlite3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, time, timedelta

# ------------------------------------------
# DATABASE (PERSISTENT STORAGE)
# ------------------------------------------
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        email TEXT,
        priority TEXT,
        due TEXT,
        reminded INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

init_db()

def add_task(title, description, email, priority, due):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, description, email, priority, due) VALUES (?, ?, ?, ?, ?)",
        (title, description, email, priority, due)
    )
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    data = c.fetchall()
    conn.close()
    return data

def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def mark_reminded(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET reminded=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

# ------------------------------------------
# SENDGRID EMAIL SENDER
# ------------------------------------------
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
FROM_EMAIL = st.secrets["FROM_EMAIL"]

def send_email(to_email, subject, content):
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=content,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

# ------------------------------------------
# STREAMLIT UI
# ------------------------------------------
st.set_page_config(page_title="AI Task Manager", layout="centered")
st.title("✨ AI Task Manager (With Email & Popup Reminders)")

page = st.sidebar.selectbox("Navigation", ["➕ Add Task", "📋 Task List"])

# ------------------------------------------
# ADD TASK PAGE
# ------------------------------------------
if page == "➕ Add Task":
    st.header("Add a New Task")

    title = st.text_input("Task Title")
    description = st.text_area("Description")
    email = st.text_input("Email to send reminder to")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    due_date = st.date_input("Due Date")
    due_time = st.time_input("Due Time", value=time(12, 0))
    due = datetime.combine(due_date, due_time).isoformat()

    if st.button("Save Task"):
        add_task(title, description, email, priority, due)
        st.success("Task added successfully! 🎉")
        st.experimental_rerun()

# ------------------------------------------
# TASK LIST PAGE
# ------------------------------------------
else:
    st.header("Your Tasks")
    tasks = get_tasks()

    if not tasks:
        st.info("No tasks found.")
    else:
        priority_color = {"Low": "green", "Medium": "orange", "High": "red"}

        for t in tasks:
            task_id, title, desc, email, priority, due_str, reminded = t
            due_time = datetime.fromisoformat(due_str)
            overdue = datetime.now() > due_time

            with st.expander(f"{title} ({priority})"):
                st.markdown(
                    f"**Description:** {desc}<br>"
                    f"📧 **Email:** {email}<br>"
                    f"⏳ **Due:** {due_time.strftime('%Y-%m-%d %H:%M')} "
                    f"{'⚠️ Overdue' if overdue else ''}<br>"
                    f"<span style='color:{priority_color[priority]}; font-weight:bold'>Priority: {priority}</span>",
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)

                # Send email manually
                with col1:
                    if st.button(f"Send Reminder Now → {task_id}", key=f"send_{task_id}"):
                        sent = send_email(
                            email,
                            f"Reminder: {title}",
                            f"<p>{desc}</p><br><p>⏳ Due: {due_time.strftime('%Y-%m-%d %H:%M')}</p>"
                        )
                        if sent:
                            st.success("Reminder email sent! 📩")

                # Delete task
                with col2:
                    if st.button(f"Delete → {task_id}", key=f"del_{task_id}"):
                        delete_task(task_id)
                        st.success("Task deleted.")
                        st.experimental_rerun()

        # ------------------------------------------
        # AUTOMATIC REMINDERS (10 MIN BEFORE DUE) + POPUP
        # ------------------------------------------
        for t in tasks:
            task_id, title, desc, email, priority, due_str, reminded = t
            due_time = datetime.fromisoformat(due_str)
            # Check if it's 10 minutes before due and not already reminded
            if not reminded and datetime.now() >= due_time - timedelta(minutes=10):
                # Send email
                sent = send_email(
                    email,
                    f"Upcoming Task Reminder: {title}",
                    f"<p>{desc}</p><br><p>⏳ Due: {due_time.strftime('%Y-%m-%d %H:%M')}</p>"
                )
                if sent:
                    mark_reminded(task_id)

                # Show popup in Streamlit
                st.warning(f"⏰ Reminder: '{title}' is due at {due_time.strftime('%H:%M')}!")
