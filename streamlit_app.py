import streamlit as st
import requests
from datetime import datetime, date, time, timezone

<<<<<<< HEAD
BASE_URL = "https://task-manager-agent.onrender.com"  # change if backend URL differs
=======
# Try to import plyer for desktop notifications (works only locally)
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ModuleNotFoundError:
    PLYER_AVAILABLE = False  # fallback for Streamlit Cloud

# Backend URL
BASE_URL = "https://task-manager-agent-api.onrender.com"
  # Use your FastAPI backend URL
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087

st.set_page_config(page_title="🧠 AI Task Manager", layout="centered")
st.title("🧠 AI Task Manager")

menu = ["Add Task", "Update Task", "Delete Task", "List Tasks"]
choice = st.sidebar.selectbox("Menu", menu)

<<<<<<< HEAD
# ---------------- ADD TASK ----------------
if choice == "Add Task":
    st.subheader("📌 Create New Task")
=======
# -------------------- Notification Function --------------------
def send_notification(title, message):
    if PLYER_AVAILABLE:
        notification.notify(title=title, message=message, timeout=5)
    else:
        st.info(f"🔔 {title}: {message}")

# -------------------- ADD TASK --------------------
if choice == "Add Task":
    st.subheader("Add a New Task")

    email = st.text_input("Your Email (for reminders)")
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
    title = st.text_input("Task Title")
    description = st.text_area("Task Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    email = st.text_input("Send Reminder To (Email)")  # <-- NEW!
    due_date = st.date_input("Due Date", min_value=date.today())
    due_time = st.time_input("Due Time", value=time(12, 0))
<<<<<<< HEAD
    remind = st.checkbox("Enable Reminder?")
    reminder_minutes = st.selectbox("Remind me before:", [5,10,15,30,60,120])
=======

    remind = st.checkbox("Send Email Reminder?")
    reminder_minutes = st.selectbox("Remind me before:", [5, 10, 15, 30, 60], index=1)
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087

    if st.button("Add Task"):
        due_dt = datetime.combine(due_date, due_time).astimezone(timezone.utc)
        
        payload = {
            "id": 0,
            "email": email,
            "title": title,
            "description": description,
            "priority": priority,
            "email": email,                        # <--- Email added
            "due": due_dt.isoformat(),
            "status": "todo",
            "remind": remind,
            "reminder_time": reminder_minutes
        }

        try:
            res = requests.post(f"{BASE_URL}/tasks", json=payload)
<<<<<<< HEAD
            st.success("Task Added Successfully 🎉")
=======
            st.success(res.json()["message"])
            if remind:
                send_notification("Task Added", f"{title} - Reminder set!")
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
        except Exception as e:
            st.error(f"❌ Error: {e}")


# ---------------- UPDATE TASK ----------------
elif choice == "Update Task":
<<<<<<< HEAD
    st.subheader("✏ Update Task")
    task_id = st.number_input("Task ID", min_value=1, step=1)
    new_title = st.text_input("New Title")
    new_desc = st.text_area("New Description")
    new_email = st.text_input("New Email")  # <-- NEW Editable email
    new_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    new_status = st.selectbox("Status", ["todo", "done"])
    new_due_date = st.date_input("New Due Date", value=date.today())
    new_due_time = st.time_input("New Due Time", value=time(12, 0))
    new_remind = st.checkbox("Enable Reminder?")
    new_reminder_minutes = st.selectbox("Reminder Before (min)", [5,10,15,30,60,120])
=======
    st.subheader("Update Task")

    task_id = st.number_input("Task ID", min_value=1, step=1)
    email = st.text_input("Your Email (for reminders)")
    new_title = st.text_input("New Title")
    new_description = st.text_area("New Description")
    new_priority = st.selectbox("New Priority", ["", "Low", "Medium", "High"])
    new_status = st.selectbox("New Status", ["", "todo", "done"])
    new_due_date = st.date_input("New Due Date", value=date.today())
    new_due_time = st.time_input("New Due Time", value=time(12, 0))
    new_remind = st.checkbox("Enable Email Reminder?")
    new_reminder_minutes = st.selectbox("Remind me before:", [5, 10, 15, 30, 60], index=1)
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087

    if st.button("Update Task"):
        payload = {
            "id": task_id,
<<<<<<< HEAD
            "title": new_title,
            "description": new_desc,
            "priority": new_priority,
            "email": new_email,                      # <-- email saved
            "due": datetime.combine(new_due_date, new_due_time).astimezone(timezone.utc).isoformat(),
            "status": new_status,
=======
            "email": email,
            "title": new_title or "No Change",
            "description": new_description or "No Change",
            "priority": new_priority or "Medium",
            "due": datetime.combine(new_due_date, new_due_time).astimezone(timezone.utc).isoformat(),
            "status": new_status or "todo",
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
            "remind": new_remind,
            "reminder_time": new_reminder_minutes
        }

        try:
            res = requests.put(f"{BASE_URL}/tasks/{task_id}", json=payload)
<<<<<<< HEAD
            st.success("Task Updated Successfully 🔄")
=======
            st.success(res.json()["message"])
            if new_remind:
                send_notification("Task Updated", f"{payload['title']} - Reminder Updated!")
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
        except Exception as e:
            st.error(f"❌ Error: {e}")


# ---------------- DELETE TASK ----------------
elif choice == "Delete Task":
<<<<<<< HEAD
    st.subheader("🗑 Delete Task")
    task_id = st.number_input("Task ID", min_value=1, step=1)
    if st.button("Delete"):
=======
    st.subheader("Delete Task")
    task_id = st.number_input("Task ID to Delete", min_value=1)

    if st.button("Delete Task"):
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
        try:
            res = requests.delete(f"{BASE_URL}/tasks/{task_id}")
            st.success("Task Deleted Successfully")
        except Exception as e:
            st.error(f"❌ Error: {e}")


# ---------------- LIST TASKS ----------------
elif choice == "List Tasks":
<<<<<<< HEAD
    st.subheader("📋 All Tasks")
=======
    st.subheader("All Tasks")

>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
    try:
        res = requests.get(f"{BASE_URL}/tasks")
        tasks = res.json()

        if not tasks:
            st.info("No Tasks Found.")
        else:
            for t in tasks:
<<<<<<< HEAD
                st.markdown(f"""
                <div style='border:1px solid #555;padding:15px;border-radius:10px;margin-bottom:10px'>
                <b>ID:</b> {t['id']}<br>
                <b>Title:</b> {t['title']}<br>
                <b>Description:</b> {t['description']}<br>
                <b>Priority:</b> {t['priority']}<br>
                <b>Email:</b> {t['email']} 📩<br>
                <b>Due:</b> {t['due']}<br>
                <b>Status:</b> {t['status']}<br>
                <b>Reminder:</b> {"Enabled" if t['remind'] else "Off"}<br>
                <b>Notify Before:</b> {t['reminder_time']} min
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
=======
                st.markdown(
                    f"""
                    <div style="border:1px solid #ccc; padding:15px; border-radius:10px; margin-bottom:10px;">
                        <b>ID:</b> {t['id']}<br>
                        <b>Title:</b> {t['title']}<br>
                        <b>Description:</b> {t['description']}<br>
                        <b>Email:</b> {t['email']}<br>
                        <b>Due:</b> {t['due']}<br>
                        <b>Priority:</b> {t['priority']}<br>
                        <b>Status:</b> {t['status']}<br>
                        <b>Remind:</b> {"🔔 Yes" if t['remind'] else "No"}<br>
                        <b>Reminder Time:</b> {t['reminder_time']} min before
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"Error fetching tasks: {e}")
>>>>>>> 1cc5813039fcf663eae7480becfb56b90763e087
