from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr]
    phone: Optional[str]
    ad_agency_name: Optional[str]
    
    