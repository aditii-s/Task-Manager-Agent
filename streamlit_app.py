import streamlit as st
import requests
from datetime import datetime, date, time

BASE_URL = "https://task-manager-agent.onrender.com"   # your backend

st.set_page_config(page_title="AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

page = st.sidebar.selectbox("Choose Page", ["Add Task", "Task List"])

# --------------- Add Task Page ---------------
if page == "Add Task":
    st.header("➕ Add New Task")

    title = st.text_input("Task Title")
    description = st.text_area("Description")
    email = st.text_input("Reminder Email 📩")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    due_date = st.date_input("Due Date", value=date.today())
    due_time = st.time_input("Due Time", value=time(12, 0))

    remind = st.checkbox("Enable Reminder")
    reminder_minutes = st.number_input("Remind Before (minutes)", min_value=0, value=15)

    if st.button("Add Task"):
        due_str = datetime.combine(due_date, due_time).isoformat()

        payload = {
            "id": 0,
            "title": title,
            "description": description,
            "email": email,
            "priority": priority,
            "due": due_str,
            "status": "todo",
            "remind": remind,
            "reminder_time": reminder_minutes
        }

        r = requests.post(f"{BASE_URL}/tasks", json=payload)

        if r.status_code == 200:
            st.success("🎉 Task added successfully!")
        else:
            st.error("Failed to add task.")

# --------------- Task List Page ---------------
elif page == "Task List":
    st.header("📋 Your Tasks")

    r = requests.get(f"{BASE_URL}/tasks")

    if r.status_code != 200:
        st.error("Failed to load tasks.")
    else:
        tasks = r.json()

        if not tasks:
            st.info("No tasks yet.")
        else:
            for task in tasks:
                with st.expander(task["title"]):
                    st.write(f"📧 **Email:** {task['email']}")
                    st.write(f"⏳ **Due:** {task['due']}")
                    st.write(f"⚡ **Priority:** {task['priority']}")
                    st.write(f"🔔 **Reminder:** {'Yes' if task['remind'] else 'No'}")

                    col1, col2 = st.columns(2)

                    with col2:
                        if st.button(f"Delete {task['id']}"):
                            requests.delete(f"{BASE_URL}/tasks/{task['id']}")
                            st.success("Deleted!")
                            st.experimental_rerun()
