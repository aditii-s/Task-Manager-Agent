import sqlite3

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
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

# Initialize DB on import
init_db()


def add_task(title, description, email, priority, due_date, due_time, remind_before):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, email, priority, due_date, due_time, remind_before) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, description, email, priority, due_date, due_time, remind_before),
    )
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def update_task(task_id, title, description, email, priority, due_date, due_time, remind_before):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE tasks SET title=?, description=?, email=?, priority=?, 
           due_date=?, due_time=?, remind_before=? WHERE id=?""",
        (title, description, email, priority, due_date, due_time, remind_before, task_id)
    )
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
