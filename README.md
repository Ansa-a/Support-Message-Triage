# FastAPI Supabase Auth & SQLite Task Manager

A secure, production-ready FastAPI backend integrated with **Supabase Auth** for user management and an **SQLite** database for user tasks, featuring robust token verification guard middleware.

---

## 🚀 What This Project Is

This project serves as a secure backend API that demonstrates modern authentication and resource management. Key features include:
* **Open Authentication**: Sign up and log in securely via Supabase Auth.
* **Token Verification Guard**: Protected routes that intercept, extract, and validate Bearer tokens using Supabase.
* **SQLite Task Management**: Perform full CRUD operations (`GET`, `POST`, `PUT`, `DELETE`) on tasks.
* **Interactive Documentation**: Fully documented via FastAPI's automatic Swagger UI (`/docs`).

---

## 🛠️ How to Set Up Your Local Environment

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/Ansa-a/Todo-fastapi.git](https://github.com/Ansa-a/Todo-fastapi.git)
   cd Todo-fastapi

2. **create virtual env**
python -m venv .venv
# On Windows (Git Bash / CMD):
source .venv/Scripts/activate
# On macOS / Linux:
source .venv/bin/activate

3. **Install Dependencies:**
pip install fastapi uvicorn pydantic python-dotenv supabase

4. **Configure Environment Variables:**
Create a .env file in the root directory and add your Supabase credentials (Never commit this file to GitHub):
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_public_key_here

**run at**
uvicorn main:app --reload