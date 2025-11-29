# app.py
import streamlit as st
import requests
from datetime import datetime, date, time, timezone

# ------------------ CONFIG ------------------
BASE_URL = "https://task-manager-agent.onrender.com"  # FastAPI backend URL

SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY")
FROM_EMAIL = st.secrets.get("FROM_EMAIL")

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager Dashboard")

menu = ["Add Task", "Update Task", "Delete Task", "List Tasks"]
choice = st.sidebar.selectbox("📌 Menu", menu)

# ================= ADD TASK =================
if choice == "Add Task":
    st.subheader("➕ Add New Task")

    title = st.text_input("Task Title")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    email = st.text_input("Email for Reminder 📩")

    due_date = st.date_input("Due Date", min_value=date.today())
    due_time = st.time_input("Due Time", value=time(12, 0))

    remind = st.checkbox("Enable Email Reminder?")
    reminder_minutes = st.selectbox("Remind Me Before:", [5, 10, 15, 30, 60, 120])

    if st.button("Add Task"):
        if not title or not email:
            st.warning("Please provide both Task Title and Email")
        else:
            due_dt = datetime.combine(due_date, due_time).astimezone(timezone.utc)
            payload = {
                "id": 0,
                "title": title,
                "description": description,
                "priority": priority,
                "email": email,
                "due": due_dt.isoformat(),
                "status": "todo",
                "remind": remind,
                "reminder_time": reminder_minutes
            }
            try:
                res = requests.post(f"{BASE_URL}/tasks", json=payload)
                if res.status_code == 200:
                    st.success("🎉 Task Added Successfully")
                else:
                    st.error(f"❌ Failed to add task: {res.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ================= UPDATE TASK =================
elif choice == "Update Task":
    st.subheader("✏ Update Task")

    task_id = st.number_input("Task ID", min_value=1, step=1)
    title = st.text_input("New Title")
    description = st.text_area("New Description")
    email = st.text_input("New Email 📩")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    status = st.selectbox("Status", ["todo", "done"])
    due_date = st.date_input("New Due Date", value=date.today())
    due_time = st.time_input("New Due Time", value=time(12, 0))
    remind = st.checkbox("Enable Reminder?")
    reminder_minutes = st.selectbox("Reminder Before (min)", [5, 10, 15, 30, 60, 120])

    if st.button("Update Task"):
        if not title or not email:
            st.warning("Please provide both Title and Email")
        else:
            payload = {
                "id": task_id,
                "title": title,
                "description": description,
                "email": email,
                "priority": priority,
                "due": datetime.combine(due_date, due_time).astimezone(timezone.utc).isoformat(),
                "status": status,
                "remind": remind,
                "reminder_time": reminder_minutes
            }
            try:
                res = requests.put(f"{BASE_URL}/tasks/{task_id}", json=payload)
                if res.status_code == 200:
                    st.success("🔄 Task Updated Successfully")
                else:
                    st.error(f"❌ Failed to update task: {res.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ================= DELETE TASK =================
elif choice == "Delete Task":
    st.subheader("🗑 Delete Task")

    task_id = st.number_input("Task ID to Delete", min_value=1, step=1)

    if st.button("Delete"):
        try:
            res = requests.delete(f"{BASE_URL}/tasks/{task_id}")
            if res.status_code == 200:
                st.success("🗑 Task Deleted Successfully")
            else:
                st.error(f"❌ Failed to delete task: {res.text}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ================= LIST TASKS =================
elif choice == "List Tasks":
    st.subheader("📋 All Tasks")
    try:
        res = requests.get(f"{BASE_URL}/tasks")
        tasks = res.json()

        if not tasks:
            st.info("No Tasks Available")
        else:
            for t in tasks:
                st.markdown(f"""
                    <div style="border:1px solid #555; padding:12px; border-radius:10px; margin-bottom:10px;">
                        <b>ID:</b> {t.get('id', 'N/A')}<br>
                        <b>Title:</b> {t.get('title', 'N/A')}<br>
                        <b>Description:</b> {t.get('description', 'N/A')}<br>
                        <b>Email:</b> {t.get('email', 'N/A')}<br>
                        <b>Priority:</b> {t.get('priority', 'N/A')}<br>
                        <b>Due:</b> {t.get('due', 'N/A')}<br>
                        <b>Status:</b> {t.get('status', 'N/A')}<br>
                        <b>Reminder:</b> {"Enabled" if t.get('remind', False) else "Off"}<br>
                        <b>Reminder Before:</b> {t.get('reminder_time', 0)} min
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
