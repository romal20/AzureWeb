import sqlite3
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

# Connect to SQLite database
conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

# Create tasks table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        created_on TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        completed_time TEXT
    )
''')
conn.commit()

# Function to create a new task
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
