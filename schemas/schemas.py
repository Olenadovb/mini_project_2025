from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    phone: str
    description: Optional[str] = None
    image_path: Optional[str] = None
    country: str
    city: str


class UserResponse(UserCreate):
    idUsers: int
    created_at: datetime

    class Config:
        from_attributes = True


class RequestCreate(BaseModel):
    name: str
    description: str
    image_path: str
    state: int
    id_author: int
    category_ids: List[int]


class RequestResponse(BaseModel):
    idRequest: int
    name: str
    description: str
    image_path: str
    created_at: datetime
    state: int

    class Config:
        from_attributes = True
