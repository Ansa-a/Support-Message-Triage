from fastapi import FastAPI, HTTPException

app = FastAPI(title="fastapi-todo", version="1.0")

# Stage 2: In-memory "database" list with 3 pre-filled tasks
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write code", "done": True},
    {"id": 3, "title": "Build API", "done": False},
]

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Stage 2: Endpoint to list all tasks
@app.get("/tasks")
def get_all_tasks():
    return tasks

# Stage 2: Endpoint to get a single task by ID with 404 error handling
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    # If the loop finishes without finding the task, raise a 404 error
    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})