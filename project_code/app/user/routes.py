from typing import Union
from fastapi import APIRouter
from utils.response_models import SuccessResponse,ErrorResponse
from utils.query_helpers import QueryHelper
from user.models import User
router = APIRouter()

@router.post("/signup", response_model=Union[SuccessResponse, ErrorResponse])
async def signup(user: User):
    """
    User signup endpoint.
    """
    user_found = QueryHelper.find_one("users", {"username": user.username})
    if user_found:
        return ErrorResponse(
            success=False,
            errors=[{"message": "Username already exists"}],
            code=409,
        )
    user= QueryHelper.insert_one("users", user.dict())
    if isinstance(user, ErrorResponse):
        return ErrorResponse(
            success=False,
            errors=[{"message": "Signup failed"}],
            code=404,
        )
    return SuccessResponse(
        success=True,
        data={"user": user},
        message="User created successfully",
        code=201,
    )

@router.post("/login", response_model=Union[SuccessResponse, ErrorResponse])
async def login(user: User):
    """
    User login endpoint.
    """
    user_found = QueryHelper.find_one(
        "users", {"username": user.username, "password": user.password}
    )
    if user_found:
        return SuccessResponse(
            success=True,
            data={"user": user_found},
            message="Login successful",
            code=200,
        )
    
    return ErrorResponse(
            success=False,
            errors=[{"message": "Invalid credentials"}],
            code=401,
        )
        

@router.get("/all_users", response_model=Union[SuccessResponse, ErrorResponse])
async def get_all_users():
    """
    Get all users endpoint.
    """
    users = QueryHelper.find("users",{"username": { "$ne": "admin"} } )
    if not users:
        return ErrorResponse(
            success=False,
            errors=[{"message": "No users found"}],
            code=404,
        )
    return SuccessResponse(
        success=True,
        data={"users": users},
        message="Users retrieved successfully",
        code=200,
    )
    
@router.delete("/delete_user/{username}", response_model=Union[SuccessResponse, ErrorResponse])
async def delete_user(username: str):
    """
    Delete user endpoint.
    """
    user_found = QueryHelper.find_one("users", {"username": username})
    if not user_found:
        return ErrorResponse(
            success=False,
            errors=[{"message": "User not found"}],
            code=404,
        )
    QueryHelper.delete_one("users", {"username": username})
    return SuccessResponse(
        success=True,
        message="User deleted successfully",
        code=200,
    )