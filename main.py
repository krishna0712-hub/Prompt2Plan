"""
main.py — Root ASGI entry point for Render, Railway, and cloud deployment.
Forwards to the FastAPI application defined in backend.main.
Allows 'uvicorn main:app' (Render's default start command) to work seamlessly.
"""
import os
import uvicorn
from backend.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port)
