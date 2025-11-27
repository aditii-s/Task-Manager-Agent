import threading
import time
import datetime
from app.tasks_db import list_tasks
from plyer import notification

def send_notification(task):
    """Send a desktop notification for a task"""
    notification.notify(
        title=f"Task Reminder: {task.title}",
        message=f"{task.description or 'No Description'}\nDue: {task.due.strftime('%Y-%m-%d %H:%M')}",
        timeout=10  # 10 seconds
    )

def reminder_scheduler():
    """Background scheduler that checks tasks every 30 seconds"""
    while True:
        tasks = list_tasks()
        now = datetime.datetime.utcnow()
        for task in tasks:
            if task.remind and task.due and task.status != "done":
                # Calculate time difference in seconds
                delta = (task.due - now).total_seconds()
                if 0 <= delta <= 60:  # Trigger notification if due within 1 minute
                    send_notification(task)
        time.sleep(30)

def start_reminder_scheduler():
    """Start scheduler in a separate daemon thread"""
    t = threading.Thread(target=reminder_scheduler, daemon=True)
    t.start()
