from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from src.routes.triage import router as triage_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Support Message Triage API",
    description="Classifies support messages using an LLM backend.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Support Triage API is running."}