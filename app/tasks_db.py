import sqlite3

DB_NAME = "tasks.db"

# Create table if it doesn't exist
def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            email TEXT,
            priority TEXT,
            due_date TEXT,
            due_time TEXT,
            remind_before INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Add new task
def add_task(title, description, email, priority, due_date, due_time, remind_before):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, email, priority, due_date, due_time, remind_before)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, email, priority, due_date, due_time, remind_before))
    conn.commit()
    conn.close()

# Fetch all tasks
def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = c.fetchall()
    conn.close()
    return tasks

# Update task
def update_task(task_id, title, description, email, priority, due_date, due_time, remind_before):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE tasks
        SET title=?, description=?, email=?, priority=?, due_date=?, due_time=?, remind_before=?
        WHERE id=?
    """, (title, description, email, priority, due_date, due_time, remind_before, task_id))
    conn.commit()
    conn.close()

# Delete task
def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

# Ensure table exists
create_table()
