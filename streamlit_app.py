# streamlit_app.py
import streamlit as st
from datetime import datetime
from task_db import init_db, add_task, get_all_tasks, update_task, delete_task
from email_utils import send_email

# Initialize DB
init_db()

st.set_page_config(page_title="Task Manager", layout="wide")
st.title("📋 Task Manager")

# ----- Add New Task -----
st.header("Add New Task")
with st.form("task_form"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    email = st.text_input("Email (optional)")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date")
    due_time = st.time_input("Due Time")
    submitted = st.form_submit_button("Save Task")
    
    if submitted:
        due = datetime.combine(due_date, due_time).isoformat()
        add_task(title, description, email, priority, due)
        st.success("Task added successfully! 🎉")
        st.experimental_rerun()

# ----- Automatic Email Reminders -----
tasks = get_all_tasks()
now = datetime.now()
for task in tasks:
    task_id, title, description, email, priority, due, reminded = task
    due_dt = datetime.fromisoformat(due)
    if not reminded and email and now >= due_dt:
        subject = f"Task Reminder: {title}"
        content = f"""
        <p>Hello,</p>
        <p>This is a reminder for your task:</p>
        <p><b>{title}</b></p>
        <p>{description}</p>
        <p>Priority: {priority}</p>
        <p>Due: {due}</p>
        """
        if send_email(email, subject, content):
            update_task(task_id, reminded=1)

# ----- Show Tasks -----
st.header("All Tasks")
tasks = get_all_tasks()
if tasks:
    for task in tasks:
        task_id, title, description, email, priority, due, reminded = task
        st.subheader(f"{title} ({priority})")
        st.write(f"📧 **Email:** {email if email else 'N/A'}")
        st.write(f"⏳ **Due:** {due}")
        st.write(f"✅ **Reminded:** {'Yes' if reminded else 'No'}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Delete {task_id}", key=f"del_{task_id}"):
                delete_task(task_id)
                st.success("Deleted!")
                st.experimental_rerun()
        with col2:
            if st.button(f"Mark Reminded {task_id}", key=f"rem_{task_id}"):
                update_task(task_id, reminded=1)
                st.success("Marked as reminded")
                st.experimental_rerun()
        with col3:
            if st.button(f"Send Email {task_id}", key=f"email_{task_id}"):
                if send_email(email, f"Task Reminder: {title}", description):
                    update_task(task_id, reminded=1)
                    st.success(f"Email sent to {email}")
else:
    st.info("No tasks found.")
