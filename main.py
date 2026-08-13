from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="fastapi-todo",
    version="1.0",
    description="A lightweight CRUD API for managing a to-do list."
)

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write code", "done": True},
    {"id": 3, "title": "Build API", "done": False},
]

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

@app.get("/tasks", summary="List All Tasks", description="Returns the complete list of tasks from memory.")
def get_all_tasks():
    return tasks

@app.get("/tasks/{task_id}", summary="Get a Single Task", description="Retrieves a specific task by its unique ID.")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a Task", description="Adds a new task with done set to false.")
def create_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    next_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": next_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", summary="Update a Task", description="Replaces a task's title and/or completion status.")
def update_task(task_id: int, payload: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if payload.title is not None:
                if not payload.title.strip():
                    raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
                task["title"] = payload.title.strip()
            if payload.done is not None:
                task["done"] = payload.done
            return task
    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a Task", description="Removes a task from memory completely.")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})