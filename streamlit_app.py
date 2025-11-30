import streamlit as st
import sqlite3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, time

# ------------------------------------------
# DATABASE (PERSISTENT STORAGE ON STREAMLIT)
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
        due TEXT
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
        return False


# ------------------------------------------
# STREAMLIT UI
# ------------------------------------------
st.set_page_config(page_title="AI Task Manager", layout="centered")
st.title("✨ AI Task Manager (With Email Reminders)")


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
    due = str(datetime.combine(due_date, due_time))

    if st.button("Save Task"):
        add_task(title, description, email, priority, due)
        st.success("Task added successfully! 🎉")


# ------------------------------------------
# TASK LIST PAGE
# ------------------------------------------
else:
    st.header("Your Tasks")
    tasks = get_tasks()

    if not tasks:
        st.info("No tasks found.")
    else:
        for t in tasks:
            task_id, title, desc, email, priority, due = t

            with st.expander(f"{title} ({priority})"):
                st.write(f"**Description:** {desc}")
                st.write(f"📧 **Email:** {email}")
                st.write(f"⏳ **Due:** {due}")

                col1, col2 = st.columns(2)

                # Send email manually
                with col1:
                    if st.button(f"Send Reminder Now → {task_id}"):
                        sent = send_email(
                            email,
                            f"Reminder: {title}",
                            f"<p>{desc}</p><br><p>⏳ Due: {due}</p>"
                        )
                        if sent:
                            st.success("Reminder email sent! 📩")
                        else:
                            st.error("Email failed. Check SendGrid settings.")

                # Delete task
                with col2:
                    if st.button(f"Delete → {task_id}"):
                        delete_task(task_id)
                        st.success("Task deleted.")
                        st.experimental_rerun()
