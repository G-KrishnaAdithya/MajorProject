from typing import Optional
from pydantic import BaseModel, EmailStr

class StoryBoard(BaseModel):
    username: Optional[str]
    story:str
    video: Optional[str]
    
    