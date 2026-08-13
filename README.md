# FastAPI To-Do List API

A lightweight, high-performance RESTful API built with Python and FastAPI to manage a to-do list through the four core CRUD operations. Developed as part of the FlyRank Backend Track (Week 2 Assignment).

---

## Features
* **In-Memory Storage**: Manages task data efficiently using a runtime Python list.
* **Full CRUD Operations**: Create, read, update, and delete tasks with proper HTTP status codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`).
* **Input Validation**: Validates requests using Pydantic to ensure task titles are never empty.
* **Interactive Documentation**: Built-in Swagger UI at `/docs`.

---

## How to Install & Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/Ansa-a/Todo-fastapi.git](https://github.com/Ansa-a/Todo-fastapi.git)
   cd Todo-fastapi