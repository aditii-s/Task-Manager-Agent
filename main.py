from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

# Load API keys and sender email from .env
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

app = FastAPI(title="AI Task Manager API")

# ==================== Task Model =====================
class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    email: str                        # 🔥 Each task has its own email
    due: Optional[str] = None
    status: str = "todo"
    remind: bool = False
    reminder_time: int = 0           # Minutes before deadline


tasks: List[Task] = []
task_counter = 1


# ==================== SendGrid Email Sender =====================
def send_email(to_email: str, subject: str, content: str):
    if not SENDGRID_API_KEY:
        print("❌ No SendGrid key found (.env missing)")
        return

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"📩 Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


# ==================== Reminder Execution =====================
def send_reminder(task_id: int):
    for t in tasks:
        if t.id == task_id:
            print(f"🔔 Reminder triggered for task {t.title}")

            email_html = f"""
            <h2>🔔 Task Reminder</h2>
            <p><b>{t.title}</b> is due soon ⏳</p>
            <p>{t.description}</p>
            <p><b>Priority:</b> {t.priority}</p>
            """

            send_email(t.email, f"Reminder: {t.title}", email_html)
            break


# ==================== Scheduler Setup =====================
scheduler = BackgroundScheduler()
scheduler.start()

def schedule_task_reminder(task: Task):
    if not task.remind or not task.due:
        return

    try:
        due = datetime.fromisoformat(task.due)
    except:
        print("⚠ Invalid date/time format")
        return

    trigger_time = due - timedelta(minutes=task.reminder_time)

    if trigger_time > datetime.now(timezone.utc):
        scheduler.add_job(
            send_reminder,
            trigger="date",
            run_date=trigger_time,
            args=[task.id],
            id=f"reminder_{task.id}",
            replace_existing=True
        )
        print(f"⏰ Reminder scheduled for {task.email} at {trigger_time}")


# ==================== API Routes =====================

@app.post("/tasks")
def add_task(task: Task):
    global task_counter
    task.id = task_counter
    tasks.append(task)
    task_counter += 1
    schedule_task_reminder(task)
    return {"message": f"Task '{task.title}' added successfully!", "task_id": task.id}


@app.get("/tasks")
def get_tasks():
    return [t.dict() for t in tasks]


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: Task):
    for i, t in enumerate(tasks):
        if t.id == task_id:
            updated.id = task_id
            tasks[i] = updated
            schedule_task_reminder(updated)
            return {"message": f"Task '{updated.title}' updated!"}
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t.id == task_id:
            tasks.pop(i)
            try:
                scheduler.remove_job(f"reminder_{task_id}")
            except:
                pass
            return {"message": f"Task '{t.title}' deleted!"}
    raise HTTPException(status_code=404, detail="Task not found")
