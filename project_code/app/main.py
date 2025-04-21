# app/main.py

import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from user.routes import router as user_router
from storyboard.routes import router as storyboard_router
from utils.response_models import ErrorResponse

app = FastAPI()

# ─── CORS ───────────────────────────────────────────────────────────────────────
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ─── API ROUTERS ────────────────────────────────────────────────────────────────
try:
    app.include_router(user_router, prefix="/user", tags=["User"])
    app.include_router(storyboard_router, prefix="/storyboard", tags=["Storyboard"])
except Exception:
    raise HTTPException(status_code=500, detail="Failed to initialize application routers")

# ─── STATIC FILES ───────────────────────────────────────────────────────────────
# Serve generated videos at /generated_videos/<filename>
app.mount(
    "/generated_videos",
    StaticFiles(directory=Path("frontend/generated_videos")),
    name="generated_videos",
)

# (Optional) Serve your entire frontend at root:
app.mount(
    "/generated_videos",
    StaticFiles(directory=Path("frontend/generated_videos")),
    name="generated_videos",
)

# 2) Serve your entire frontend (HTML/CSS/JS) at the root
app.mount(
    "/",
    StaticFiles(directory=Path("frontend"), html=True),
    name="frontend",
)

# ─── ROOT HEALTHCHECK ──────────────────────────────────────────────────────────
@app.get("/")
async def serve_index() -> Dict[str, Any]:
    return {"message": "Server running"}

