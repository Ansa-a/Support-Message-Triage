from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="fastapi-todo", version="1.0")

# In-memory "database" list
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write code", "done": True},
    {"id": 3, "title": "Build API", "done": False},
]

# Stage 3: Pydantic model to validate incoming POST data
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_all_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})

# Stage 3: Create a new task with validation and 201 status code
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    # Check if title is just empty spaces after stripping
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    # Generate next ID automatically
    next_id = max([t["id"] for t in tasks], default=0) + 1
    
    new_task = {
        "id": next_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks.append(new_task)
    return new_task