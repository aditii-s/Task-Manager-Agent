from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

app = FastAPI(title="AI Task Manager API")

@app.get("/healthz")
def health():
    return {"status": "ok"}

class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    email: str
    due: Optional[str] = None
    status: str = "todo"
    remind: bool = False
    reminder_time: int = 0

tasks: List[Task] = []
task_counter = 1


def send_email(to_email: str, subject: str, content: str):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        print("❌ Missing SendGrid credentials.")
        return False
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print("Email sent to", to_email)
        return True
    except Exception as e:
        print("Email failed:", e)
        return False


def send_reminder(task_id: int):
    for task in tasks:
        if task.id == task_id:
            subject = f"Reminder: {task.title}"
            content = f"<p>Due: {task.due}</p>"
            send_email(task.email, subject, content)
            return


scheduler = BackgroundScheduler()
scheduler.start()


def schedule_task_reminder(task: Task):
    if not task.remind or not task.due:
        return

    due_dt = datetime.fromisoformat(task.due)
    remind_at = due_dt - timedelta(minutes=task.reminder_time)
    remind_at = remind_at.replace(tzinfo=timezone.utc)

    if remind_at > datetime.now(timezone.utc):
        scheduler.add_job(
            send_reminder,
            trigger="date",
            run_date=remind_at,
            args=[task.id],
            id=f"task_{task.id}_reminder",
            replace_existing=True
        )


@app.post("/tasks")
def add_task(task: Task):
    global task_counter
    task.id = task_counter
    tasks.append(task)
    task_counter += 1
    schedule_task_reminder(task)
    return {"message": "Task added!", "task_id": task.id}


@app.get("/tasks")
def get_tasks():
    return [t.dict() for t in tasks]


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: Task):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated.id = task_id
            tasks[i] = updated

            try:
                scheduler.remove_job(f"task_{task_id}_reminder")
            except:
                pass

            schedule_task_reminder(updated)
            return {"message": "Task updated!"}

    raise HTTPException(404, "Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            try:
                scheduler.remove_job(f"task_{task_id}_reminder")
            except:
                pass
            return {"message": "Task deleted!"}

    raise HTTPException(404, "Task not found")

