from fastapi import FastAPI, status
import sqlalchemy
import databases
import os
import urllib
from datetime import datetime

host_server = os.environ.get('host_server', 'localhost')
db_server_port = str(os.environ.get('db_server_port', '5432'))
database_name = os.environ.get('database_name', 'fastapi')
db_username = str(os.environ.get('db_username', 'postgres'))
db_password = str(os.environ.get('db_password', 'secret'))
ssl_mode = str(os.environ.get('ssl_mode','prefer'))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

app = FastAPI()


notes = sqlalchemy.Table(
    "todo",
    metadata,
    sqlalchemy.Column("task_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("task_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created_on", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("status", sqlalchemy.String, default='Pending'),
    sqlalchemy.Column("completed_time", sqlalchemy.String, nullable=True)
)

engine = sqlalchemy.create_engine(
    #DATABASE_URL, connect_args={"check_same_thread": False}
    DATABASE_URL, pool_size=3, max_overflow=0
)

metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/create")
def create_task(task_name):
    created_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO tasks (task_name, created_on) VALUES (?, ?)
    ''', (task_name, created_on))
    conn.commit()
    print("Task created successfully.")

# Function to see all tasks
@app.get("/see")
def see_all_tasks():
    cursor.execute('''
        SELECT task_id, task_name, created_on, status, completed_time FROM tasks
    ''')
    tasks = cursor.fetchall()
    
    # Display headings
    headings = ["ID", "Task Name", "Created On", "Status", "Completed Time"]
    print("\n--- All Tasks ---")
    print(f"{headings[0]:<10} {headings[1]:<30} {headings[2]:<45} {headings[3]:<30} {headings[4]:<25}")
    
    # Display task details
    for task in tasks:
        task_id = task[0] if task[0] is not None else ""
        task_name = task[1] if task[1] is not None else ""
        created_on = task[2] if task[2] is not None else ""
        status = task[3] if task[3] is not None else ""
        completed_time = task[4] if task[4] is not None else ""
        
        print(f"{task_id:<10} {task_name:<30} {created_on:<40} {status:<30} {completed_time:<25}")

# Function to delete a task
@app.get("/delete")
def delete_task(task_id):
    cursor.execute('''
        SELECT * FROM tasks WHERE task_id = ?
    ''', (task_id,))
    task = cursor.fetchone()
    
    if task is None:
        print("Invalid task ID. Task not found.")
    else:
        cursor.execute('''
            DELETE FROM tasks WHERE task_id = ?
        ''', (task_id,))
        conn.commit()
        print("Task deleted successfully.")
        
        # Renumber the IDs after deletion
        cursor.execute('''
            UPDATE tasks SET task_id = task_id - 1 WHERE task_id > ?
        ''', (task_id,))
        conn.commit()
        print("IDs renumbered successfully.")

# Function to mark task as completed
@app.get("/mark")
def mark_task_completed(task_id):
    completed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        UPDATE tasks SET status = 'Completed', completed_time = ? WHERE task_id = ?
    ''', (completed_time, task_id))
    conn.commit()
    print("Task marked as completed.")

# User Interface
while True:
    print("\nTo-Do List")
    print("1. Create Task")
    print("2. See All Tasks")
    print("3. Delete Task")
    print("4. Mark Task as Completed")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        task_name = input("Enter task name: ")
        create_task(task_name)
    elif choice == '2':
        see_all_tasks()
    elif choice == '3':
        task_id = int(input("Enter task ID to delete: "))
        delete_task(task_id)
    elif choice == '4':
        task_id = int(input("Enter task ID to mark as completed: "))
        mark_task_completed(task_id)
    elif choice == '5':
        break
    else:
        print("Invalid choice. Please try again.")

