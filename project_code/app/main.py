from fastapi import FastAPI
from app.routers import script_router, image_router, user_router, export_router, feedback_router

app = FastAPI()

app.include_router(script_router.router)
app.include_router(image_router.router)
app.include_router(user_router.router)
app.include_router(export_router.router)
app.include_router(feedback_router.router)