# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

# ==================== INITIAL SETUP =====================

# Load environment variables from Render (.env not required for Render)
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

app = FastAPI(title="AI Task Manager API")

@app.get("/healthz")
def health():
    return {"status": "ok"}

# ==================== DATA MODEL =====================

class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    email: str                    # Task-specific email
    due: Optional[str] = None
    status: str = "todo"
    remind: bool = False
    reminder_time: int = 0        # Minutes before deadline

tasks: List[Task] = []
task_counter = 1

# ==================== EMAIL SENDER (FIXED) =====================

def send_email(to_email: str, subject: str, content: str):
    """Send email using SendGrid."""

    if not SENDGRID_API_KEY or not FROM_EMAIL:
        print("❌ Missing SENDGRID_API_KEY or FROM_EMAIL. Email not sent.")
        return False

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"📩 Email sent: {response.status_code} to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# ==================== REMINDER LOGIC =====================

def send_reminder(task_id: int):
    """Triggered by scheduler when reminder time is reached."""
    for task in tasks:
        if task.id == task_id:
            subject = f"🔔 Reminder: {task.title} is due soon"
            content = f"""
            <h3>Your Task Reminder</h3>
            <p><b>Task:</b> {task.title}</p>
            <p><b>Description:</b> {task.description}</p>
            <p><b>Due:</b> {task.due}</p>
            """

            send_email(task.email, subject, content)
            print(f"⏰ Reminder sent for Task {task_id}")
            return

# ==================== SCHEDULER =====================

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_task_reminder(task: Task):
    """Schedule reminder for a task if enabled."""

    if not task.remind or not task.due:
        return

    try:
        due_dt = datetime.fromisoformat(task.due)
    except Exception:
        print("⚠ Invalid due datetime format. Use: YYYY-MM-DDTHH:MM:SS")
        return

    remind_at = due_dt - timedelta(minutes=task.reminder_time)

    # Convert to UTC for safe scheduling
    if remind_at.tzinfo is None:
        remind_at = remind_at.replace(tzinfo=timezone.utc)

    # Only schedule if reminder is in future
    if remind_at > datetime.now(timezone.utc):
        scheduler.add_job(
            send_reminder,
            trigger="date",
            run_date=remind_at,
            args=[task.id],
            id=f"task_{task.id}_reminder",
            replace_existing=True
        )
        print(f"⏰ Reminder scheduled: Task {task.id} at {remind_at}")
    else:
        print("⚠ Reminder time already passed. Not scheduling.")

# ==================== API ROUTES =====================

@app.post("/tasks")
def add_task(task: Task):
    global task_counter

    task.id = task_counter
    tasks.append(task)
    task_counter += 1

    schedule_task_reminder(task)

    return {"message": f"Task '{task.title}' added!", "task_id": task.id}


@app.get("/tasks")
def get_tasks():
    return [t.dict() for t in tasks]


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: Task):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated.id = task_id
            tasks[index] = updated

            # Replace old reminder with new one
            try:
                scheduler.remove_job(f"task_{task_id}_reminder")
            except:
                pass

            schedule_task_reminder(updated)

            return {"message": f"Task '{updated.title}' updated!"}

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            try:
                scheduler.remove_job(f"task_{task_id}_reminder")
            except:
                pass
            return {"message": f"Task deleted!"}

    raise HTTPException(status_code=404, detail="Task not found")


