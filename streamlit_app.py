# streamlit_app.py
import streamlit as st
from datetime import datetime
from task_db import init_db, add_task, get_all_tasks, update_task, delete_task

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

# ----- Show Tasks -----
st.header("All Tasks")

tasks = get_all_tasks()
if tasks:
    for task in tasks:
        task_id, title, description, email, priority, due, reminded = task
        st.subheader(f"{title} ({priority})")
        st.write(f"📧 **Email:** {email if email else 'N/A'}")
        st.write(f"⏳ **Due:** {due}")
        
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
                st.info(f"Email sent to {email} (placeholder)")
