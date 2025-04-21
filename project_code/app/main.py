import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from user.routes import router as user_router
from storyboard.routes import router as storyboard_router
from utils.response_models import ErrorResponse

app = FastAPI()


# Configure CORS with proper security settings
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with proper error handling
try:
    app.include_router(user_router, prefix="/user", tags=["User"])
    app.include_router(storyboard_router, prefix="/storyboard", tags=["Storyboard"])

except Exception as e:
    raise HTTPException(
        status_code=500, detail="Failed to initialize application routers"
    )

@app.get("/")
async def serve_index() -> Dict[str, Any]:
    try:

        return {
            "message": "Server running",
        }
    except Exception as e:
        
        return ErrorResponse(
            message="Internal server error", code=500, errors=[{"detail": str(e)}]
        )
