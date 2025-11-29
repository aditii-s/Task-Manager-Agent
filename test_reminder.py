from main import tasks, send_reminder
from datetime import datetime, timezone

# Step 1: Create a test task if none exist
if not tasks:
    from main import Task, task_counter
    test_task = Task(
        id=task_counter,
        title="Test Reminder",
        email="YOUR_EMAIL_HERE",  # <-- Replace with your email
        description="This is a test reminder email.",
        priority="High",
        due=datetime.now(timezone.utc).isoformat(),
        status="todo",
        remind=True,
        reminder_time=0
    )
    tasks.append(test_task)

# Step 2: Trigger reminder manually
send_reminder(tasks[-1].id)
