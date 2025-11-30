import streamlit as st
from tasks_db import init_db, add_task, get_all_tasks, update_task, delete_task
from datetime import datetime

# ----------------------------
# Initialize DB
# ----------------------------
init_db()

# ----------------------------
# Sidebar page selector
# ----------------------------
page = st.sidebar.selectbox("Navigate", ["Add Task", "All Tasks"])

# ----------------------------
# Add Task Page
# ----------------------------
if page == "Add Task":
    st.title("➕ Add Task")

    with st.form("add_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        email = st.text_input("Email")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        due_date = st.date_input("Due Date")
        due_time = st.time_input("Due Time")
        due = datetime.combine(due_date, due_time).isoformat()

        submitted = st.form_submit_button("Save Task")
        if submitted:
            add_task(title, description, email, priority, due)
            st.success("Task added successfully!")

# ----------------------------
# All Tasks Page
# ----------------------------
elif page == "All Tasks":
    st.title("📋 All Tasks")
    tasks = get_all_tasks()

    if not tasks:
        st.info("No tasks found.")
    else:
        for task in tasks:
            task_id, title, description, email, priority, due, reminded = task

            with st.container():
                st.markdown(f"### {title} {'✅' if reminded else ''}")
                st.write(f"**Description:** {description}")
                st.write(f"**Email:** {email}")
                st.write(f"**Priority:** {priority}")
                st.write(f"**Due:** {due}")
                st.write(f"**Reminded:** {'Yes' if reminded else 'No'}")

                col1, col2 = st.columns(2)

                # Mark as reminded
                with col1:
                    if st.button("Mark as Reminded", key=f"remind_{task_id}"):
                        update_task(task_id, reminded=1)
                        st.experimental_rerun()

                # Delete task
                with col2:
                    if st.button("Delete Task", key=f"delete_{task_id}"):
                        delete_task(task_id)
                        st.experimental_rerun()
