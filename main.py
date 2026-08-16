import sqlite3
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="fastapi-todo",
    version="1.0",
    description="A lightweight CRUD API for managing a SQLite database."
)

DB_FILE = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_tasks = [
            ("Buy milk", 0),
            ("Write code", 1),
            ("Build API", 0)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", sample_tasks)
        conn.commit()
        
    conn.close()

# Initialize the database and seed data on startup
init_db()

# Helper function to get a database connection and return rows as dictionaries
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    # This allows us to access columns by name like a dictionary
    conn.row_factory = sqlite3.Row
    return conn

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    done: Optional[bool] = None

@app.get("/", summary="Root Endpoint", description="Returns basic API metadata and available endpoints.")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check", description="Verifies that the server is up and running.")
def health_check():
    return {"status": "ok"}

@app.get("/tasks", summary="List All Tasks", description="Returns the complete list of tasks from SQLite.")
def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        tasks.append({
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        })
    return tasks

@app.get("/tasks/{task_id}", summary="Get a Single Task", description="Retrieves a specific task by its unique ID from SQLite.")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})
        
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }
    
@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a Task", description="Adds a new task to the SQLite database with done set to false.")
def create_task(payload: TaskCreate):
    # Validation carried over from Assignment 1
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Stage 2: Insert into database using parameterized query
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (payload.title.strip(), 0))
    conn.commit()
    
    # Grab the auto-assigned ID from the database
    new_task_id = cursor.lastrowid
    conn.close()
    
    # Return the newly created task representation
    return {
        "id": new_task_id,
        "title": payload.title.strip(),
        "done": False
    }
