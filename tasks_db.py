# task_db.py
import sqlite3

DB_NAME = "tasks.db"

def init_db():
    """Initialize the database and create tasks table if it doesn't exist"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        email TEXT,
        priority TEXT,
        due TEXT,
        reminded INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_task(title, description, email, priority, due):
    """Add a new task"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, description, email, priority, due, reminded) VALUES (?, ?, ?, ?, ?, 0)",
        (title, description, email, priority, due)
    )
    conn.commit()
    conn.close()

def get_all_tasks():
    """Return all tasks"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    rows = c.fetchall()
    conn.close()
    return rows

def update_task(task_id, **kwargs):
    """Update a task column(s)"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE tasks SET {key}=? WHERE id=?", (value, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Delete a task"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

