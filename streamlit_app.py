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

            with st.expander(f"{title} {'✅' if reminded else ''}"):
                st.write(f"**Description:** {description}")
                st.write(f"**Email:** {email}")
                st.write(f"**Priority:** {priority}")
                st.write(f"**Due:** {due}")
                st.write(f"**Reminded:** {'Yes' if reminded else 'No'}")

                col1, col2, col3 = st.columns(3)

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

                # Edit task
                with col3:
                    if st.button("Edit Task", key=f"edit_{task_id}"):
                        st.session_state.editing_task = task_id

        # ----------------------------
        # Editing Task Form
        # ----------------------------
        if "editing_task" in st.session_state:
            edit_id = st.session_state.editing_task
            edit_task = next(t for t in tasks if t[0] == edit_id)
            _, e_title, e_description, e_email, e_priority, e_due, e_reminded = edit_task

            st.markdown("---")
            st.subheader("✏️ Edit Task")

            with st.form("edit_task_form"):
                new_title = st.text_input("Title", e_title)
                new_description = st.text_area("Description", e_description)
                new_email = st.text_input("Email", e_email)
                new_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(e_priority))
                new_due_datetime = datetime.fromisoformat(e_due)
                new_due_date = st.date_input("Due Date", new_due_datetime.date())
                new_due_time = st.time_input("Due Time", new_due_datetime.time())
                new_due = datetime.combine(new_due_date, new_due_time).isoformat()

                save_edit = st.form_submit_button("Save Changes")
                if save_edit:
                    update_task(
                        edit_id,
                        title=new_title,
                        description=new_description,
                        email=new_email,
                        priority=new_priority,
                        due=new_due
                    )
                    st.success("Task updated successfully!")
                    del st.session_state.editing_task
                    st.experimental_rerun()

