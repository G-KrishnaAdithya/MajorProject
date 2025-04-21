from typing import Union
from fastapi import APIRouter
from utils.response_models import SuccessResponse,ErrorResponse
from utils.query_helpers import QueryHelper
from storyboard.models import StoryBoard
from storyboard.services import generate_storyboard_video
router = APIRouter()

@router.post("/generate", response_model=Union[SuccessResponse, ErrorResponse])
async def generate_storyboard_endpoint(storyboard:StoryBoard):
    name = storyboard.username
    story = storyboard.story
    link = generate_storyboard_video(storyboard.story)
    QueryHelper.insert_one(
        "storyboards",
        {
            "story": story,
            "username": name,
            "video": link.replace("frontend/",""),
        }
    )
    return SuccessResponse(
        success=True,
        data={"username": name, "story": story, "video": link},
        message="Storyboard generated successfully",
        code=201,
    )

@router.get("/get_storyboards", response_model=Union[SuccessResponse, ErrorResponse])
async def get_storyboard_endpoint(username: str):
    results = QueryHelper.find(
        "storyboards",
        {
            "username": username
        }
    )
    if results:
        return SuccessResponse(
            success=True,
            data=results,
            code =200,
            message="Storyboards retrieved successfully"
            )
    else:
        return ErrorResponse(message="No storyboard found for this user.")
    