import sqlite3

DB_NAME = "tasks.db"

# ----------------------------
# Initialize DB
# ----------------------------
def init_db():
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

# ----------------------------
# Add a task
# ----------------------------
def add_task(title, description, email, priority, due):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, email, priority, due, reminded)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (title, description, email, priority, due))
    conn.commit()
    conn.close()

# ----------------------------
# Get all tasks
# ----------------------------
def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, description, email, priority, due, reminded FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return tasks

# ----------------------------
# Update task (any field)
# ----------------------------
def update_task(task_id, title=None, description=None, email=None, priority=None, due=None, reminded=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    updates = []
    values = []

    if title is not None:
        updates.append("title = ?")
        values.append(title)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    if email is not None:
        updates.append("email = ?")
        values.append(email)
    if priority is not None:
        updates.append("priority = ?")
        values.append(priority)
    if due is not None:
        updates.append("due = ?")
        values.append(due)
    if reminded is not None:
        updates.append("reminded = ?")
        values.append(reminded)

    values.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    c.execute(sql, values)
    conn.commit()
    conn.close()

# ----------------------------
# Delete task
# ----------------------------
def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
