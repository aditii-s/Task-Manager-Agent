from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

app = FastAPI(title="AI Task Manager API")

# -------------------- Task Model --------------------
class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    due: Optional[str] = None
    status: str = "todo"
    remind: bool = False
    reminder_time: int = 0

tasks: List[Task] = []
task_counter = 1

# -------------------- CRUD Endpoints --------------------
@app.post("/tasks")
def add_task(task: Task):
    global task_counter
    task.id = task_counter
    tasks.append(task)
    task_counter += 1
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
            return {"message": f"Task '{updated.title}' updated successfully!"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t.id == task_id:
            tasks.pop(i)
            return {"message": f"Task '{t.title}' deleted successfully!"}
    raise HTTPException(status_code=404, detail="Task not found")
