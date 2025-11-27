import streamlit as st
import requests
from datetime import datetime, date, time, timezone

# Try to import plyer for desktop notifications
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ModuleNotFoundError:
    PLYER_AVAILABLE = False  # fallback for Streamlit Cloud

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager")

menu = ["Add Task", "Update Task", "Delete Task", "List Tasks"]
choice = st.sidebar.selectbox("Menu", menu)

# Function to send notifications
def send_notification(title, message):
    if PLYER_AVAILABLE:
        notification.notify(
            title=title,
            message=message,
            timeout=5
        )
    else:
        # Fallback for Streamlit Cloud
        st.info(f"🔔 {title}: {message}")

# -------------------- ADD TASK --------------------
if choice == "Add Task":
    st.subheader("Add a New Task")
    title = st.text_input("Task Title")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date", min_value=date.today())
    due_time = st.time_input("Due Time", value=time(12, 0))
    remind = st.checkbox("Send Reminder? (Desktop & Email)")
    reminder_minutes = st.selectbox("Remind me before:", [0, 5, 10, 15, 30, 60], index=0)

    if st.button("Add Task"):
        due_dt = datetime.combine(due_date, due_time).astimezone(timezone.utc)
        payload = {
            "id": 0,
            "title": title,
            "description": description,
            "priority": priority,
            "due": due_dt.isoformat(),
            "status": "todo",
            "remind": remind,
            "reminder_time": reminder_minutes
        }
        try:
            res = requests.post(f"{BASE_URL}/tasks", json=payload)
            st.success(res.json()["message"])
            if remind:
                send_notification(f"Task Added: {title}", f"{description} - Due {due_dt}")
        except Exception as e:
            st.error(f"Error adding task: {e}")

# -------------------- UPDATE TASK --------------------
elif choice == "Update Task":
    st.subheader("Update Task")
    task_id = st.number_input("Task ID", min_value=1, step=1)
    new_title = st.text_input("New Title (optional)")
    new_description = st.text_area("New Description (optional)")
    new_priority = st.selectbox("New Priority (optional)", ["", "Low", "Medium", "High"])
    new_status = st.selectbox("Status", ["", "todo", "done"])
    new_due_date = st.date_input("New Due Date (optional)", value=date.today())
    new_due_time = st.time_input("New Due Time (optional)", value=time(12, 0))
    new_remind = st.checkbox("Send Reminder? (Desktop & Email)")
    new_reminder_minutes = st.selectbox("Remind me before:", [0, 5, 10, 15, 30, 60], index=0)

    if st.button("Update Task"):
        payload = {
            "id": task_id,
            "title": new_title if new_title else "No Change",
            "description": new_description if new_description else "No Change",
            "priority": new_priority if new_priority else "Medium",
            "due": datetime.combine(new_due_date, new_due_time).astimezone(timezone.utc).isoformat(),
            "status": new_status if new_status else "todo",
            "remind": new_remind,
            "reminder_time": new_reminder_minutes
        }
        try:
            res = requests.put(f"{BASE_URL}/tasks/{task_id}", json=payload)
            st.success(res.json()["message"])
            if new_remind:
                send_notification(f"Task Updated: {payload['title']}", f"{payload['description']} - Due {payload['due']}")
        except Exception as e:
            st.error(f"Error updating task: {e}")

# -------------------- DELETE TASK --------------------
elif choice == "Delete Task":
    st.subheader("Delete Task")
    task_id = st.number_input("Task ID to Delete", min_value=1, step=1)
    if st.button("Delete Task"):
        try:
            res = requests.delete(f"{BASE_URL}/tasks/{task_id}")
            st.success(res.json()["message"])
        except Exception as e:
            st.error(f"Error deleting task: {e}")

# -------------------- LIST TASKS --------------------
elif choice == "List Tasks":
    st.subheader("All Tasks")
    try:
        res = requests.get(f"{BASE_URL}/tasks")
        tasks = res.json()
        if not tasks:
            st.info("No tasks found.")
        else:
            for t in tasks:
                st.markdown(
                    f"""
                    <div style="border:1px solid #ccc; padding:15px; border-radius:10px; margin-bottom:10px;">
                        <b>ID:</b> {t['id']}<br>
                        <b>Title:</b> {t['title']}<br>
                        <b>Description:</b> {t['description']}<br>
                        <b>Due:</b> {t['due'] if t['due'] else 'N/A'}<br>
                        <b>Priority:</b> {t['priority']}<br>
                        <b>Status:</b> {t['status']}<br>
                        <b>Remind:</b> {"🔔" if t.get('remind') else "No"}<br>
                        <b>Reminder Time:</b> {t.get('reminder_time', 0)} min before
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Send notifications
                if t.get("remind"):
                    send_notification(f"Task Reminder: {t['title']}", f"{t['description']} - Due {t['due']}")
    except Exception as e:
        st.error(f"Error fetching tasks: {e}")
