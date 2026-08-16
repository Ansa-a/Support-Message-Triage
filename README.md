# FastAPI To-Do List API

A lightweight, database-backed RESTful API built with Python and FastAPI to manage a to-do list through the four core CRUD operations. Developed as part of the FlyRank Backend Track (Week 3 Assignment).

---

## Features
* **SQLite Persistence**: Stores tasks in a local SQLite database (`tasks.db`) so your data survives server restarts.
* **Automatic Setup**: The database file and `tasks` table are created automatically on startup, pre-seeded with initial example tasks if empty.
* **Full CRUD Operations**: Create, read, update, and delete tasks with proper HTTP status codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`).
* **Parameterized Queries**: Uses secure SQL parameters (`?`) to prevent SQL injection.
* **Input Validation**: Validates requests using Pydantic to ensure task titles are never empty.
* **Interactive Documentation**: Built-in Swagger UI available at `/docs`.

---

## Why SQLite?
* **Zero Configuration**: Requires no separate server installation or external background services[cite: 1].
* **Single File Storage**: The entire database lives in one local file (`tasks.db`), making it easy to manage and test[cite: 1].

---

## How to Install & Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/Ansa-a/Todo-fastapi.git](https://github.com/Ansa-a/Todo-fastapi.git)
   cd Todo-fastapi
2. install dependencies
pip install fastapi uvicorn
3. start the server
uvicorn main:app --reload