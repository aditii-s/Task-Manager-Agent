import streamlit as st
from task_db import add_task, get_all_tasks, update_task, delete_task
from datetime import datetime

st.set_page_config(page_title="AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose Page", ["Add Task", "Task List"])

# -------------------- Add Task Page --------------------
if page == "Add Task":
    st.header("➕ Add New Task")
    title = st.text_input("Task Title")
    description = st.text_area("Description")
    email = st.text_input("Email for Reminder 📩")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date")
    due_time = st.time_input("Due Time")
    remind_before = st.number_input("Remind Me Before (minutes)", min_value=0, value=15)

    if st.button("Add Task"):
        add_task(title, description, email, priority, str(due_date), str(due_time), remind_before)
        st.success("🎉 Task Added Successfully")

# -------------------- Task List Page --------------------
elif page == "Task List":
    st.header("📋 All Tasks")
    tasks = get_all_tasks()

    if not tasks:
        st.info("No tasks found. Add a task first!")
    else:
        for task in tasks:
            task_id, title, description, email, priority, due_date, due_time, remind_before = task

            with st.expander(f"{title} ({priority})"):
                st.write(f"**Description:** {description}")
                st.write(f"**Email:** {email}")
                st.write(f"**Due:** {due_date} {due_time}")
                st.write(f"**Remind Before:** {remind_before} min")

                # Columns for Update / Delete
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Update {task_id}"):
                        # Prefill form for update
                        new_title = st.text_input("New Title", value=title, key=f"title_{task_id}")
                        new_desc = st.text_area("New Description", value=description, key=f"desc_{task_id}")
                        new_email = st.text_input("New Email", value=email, key=f"email_{task_id}")
                        new_priority = st.selectbox("New Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(priority), key=f"priority_{task_id}")
                        new_due_date = st.date_input("New Due Date", value=datetime.strptime(due_date, "%Y-%m-%d").date(), key=f"date_{task_id}")
                        new_due_time = st.time_input("New Due Time", value=datetime.strptime(due_time, "%H:%M:%S").time(), key=f"time_{task_id}")
                        new_remind_before = st.number_input("New Remind Before", value=remind_before, key=f"remind_{task_id}")

                        if st.button("Save", key=f"save_{task_id}"):
                            update_task(task_id, new_title, new_desc, new_email, new_priority,
                                        str(new_due_date), str(new_due_time), new_remind_before)
                            st.success("✅ Task Updated Successfully")
                            st.experimental_rerun()

                with col2:
                    if st.button(f"Delete {task_id}"):
                        delete_task(task_id)
                        st.success("❌ Task Deleted Successfully")
                        st.experimental_rerun()

