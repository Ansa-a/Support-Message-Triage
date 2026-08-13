from fastapi import FastAPI

# Create the app instance (this is our server "box")
app = FastAPI()

# 1. The root endpoint
@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# 2. The health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}