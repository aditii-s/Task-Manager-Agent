# tasks_db.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    due = Column(DateTime)
    priority = Column(String, default='Medium')
    status = Column(String, default='todo')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    remind = Column(Boolean, default=False)
    reminder_time = Column(DateTime, nullable=True)  # <-- NEW COLUMN

engine = create_engine('sqlite:///tasks.db', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def add_task(title, description=None, due=None, priority='Medium', remind=False, reminder_time=None):
    session = Session()
    task = Task(title=title, description=description, due=due, priority=priority, remind=remind, reminder_time=reminder_time)
    session.add(task)
    session.commit()
    session.refresh(task)
    session.close()
    return task

def list_tasks():
    session = Session()
    tasks = session.query(Task).order_by(Task.due.asc().nulls_last()).all()
    session.close()
    return tasks

def update_task(task_id, **kwargs):
    session = Session()
    task = session.query(Task).get(task_id)
    for k, v in kwargs.items():
        setattr(task, k, v)
    session.commit()
    session.refresh(task)
    session.close()
    return task

def delete_task(task_id):
    session = Session()
    task = session.query(Task).get(task_id)
    if task:
        session.delete(task)
        session.commit()
    session.close()
    return task
