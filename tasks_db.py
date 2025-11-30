import sqlite3

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table with all required columns
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
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
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, email, priority, due, reminded)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (title, description, email, priority, due))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, description, email, priority, due, reminded FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return tasks

def update_task(task_id, **kwargs):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE tasks SET {key}=? WHERE id=?", (value, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
