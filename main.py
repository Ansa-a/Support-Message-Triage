import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Security scheme for Swagger UI Bearer token integration
security = HTTPBearer()

app = FastAPI(
    title="fastapi-supabase-auth",
    version="2.0",
    description="A secure FastAPI backend integrated with Supabase Auth and SQLite tasks."
)

DB_FILE = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Pydantic Models for Auth & Tasks ---
class SignUpRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    done: Optional[bool] = None

# --- Dependency / Middleware Guard for Token Verification ---
def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Stage 3 & 4 Guard: Extracts the bearer token, verifies it via Supabase,
    and returns the authenticated user's metadata or raises 401.
    """
    token = credentials.credentials
    try:
        # Ask Supabase if the token is valid
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"}
            )
        return user_response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )

# --- Routes ---

@app.get("/", summary="Root Endpoint")
def read_root():
    return {"name": "FlyRank Auth API", "version": "2.0", "endpoints": ["/auth/signup", "/auth/login", "/protected/profile"]}

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok", "supabase_connected": True}

# --- Stage 1: Auth Endpoints ---

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, summary="Sign Up")
def signup(payload: SignUpRequest):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail={"error": "Email and password are required"})
    
    try:
        response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password
        })
        return {"message": "User created successfully", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

@app.post("/auth/login", status_code=status.HTTP_200_OK, summary="Log In")
def login(payload: LoginRequest):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail={"error": "Email and password are required"})
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail={"error": "Invalid login credentials"})

# --- Stage 2 & 3: Public and Protected Gates ---

@app.get("/public/info", status_code=status.HTTP_200_OK, summary="Public Info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile", status_code=status.HTTP_200_OK, summary="Protected Profile")
def protected_profile(user: dict = Depends(verify_bearer_token)):
    """
    Protected route verified via Supabase Auth token.
    """
    return {
        "message": "Access granted to secure profile",
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Log Out")
def logout(user: dict = Depends(verify_bearer_token)):
    try:
        supabase.auth.sign_out()
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    # --- Stage 2 & 3: Task CRUD Endpoints (Protected Sanctuary) ---

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(payload: TaskCreate, user: dict = Depends(verify_bearer_token)):
    """
    Create a new task for the authenticated user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (payload.title, 0)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, "title": payload.title, "done": False}

@app.get("/tasks", status_code=status.HTTP_200_OK, summary="Get All Tasks")
def get_tasks(user: dict = Depends(verify_bearer_token)):
    """
    Retrieve all tasks from the SQLite database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    tasks = [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]
    return tasks

@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, summary="Update Task")
def update_task(task_id: int, payload: TaskUpdate, user: dict = Depends(verify_bearer_token)):
    """
    Update an existing task's title or completion status.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    if not task:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    
    new_title = payload.title if payload.title is not None else task["title"]
    new_done = int(payload.done) if payload.done is not None else task["done"]
    
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": new_title, "done": bool(new_done)}

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(task_id: int, user: dict = Depends(verify_bearer_token)):
    """
    Delete a task by its ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    if not task:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return None