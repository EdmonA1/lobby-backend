from pydantic import BaseModel, Field
from typing import List, Optional

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: str
    age: int = Field(ge=18, le=60)
    gender: str
    city: str
    games: List[str] = []
    bio: Optional[str] = ""
    discord: Optional[str] = ""
    photos: List[str] = []
    looking_for: List[str] = []
    filter_gender: Optional[str] = "any"
    filter_age_min: int = 18
    filter_age_max: int = 60

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=60)
    gender: Optional[str] = None
    city: Optional[str] = None
    games: Optional[List[str]] = None
    bio: Optional[str] = None
    discord: Optional[str] = None
    photos: Optional[List[str]] = None
    looking_for: Optional[List[str]] = None
    filter_gender: Optional[str] = None
    filter_age_min: Optional[int] = None
    filter_age_max: Optional[int] = None

class UserPublic(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: str
    age: int
    gender: str
    city: str
    games: List[str] = []
    bio: Optional[str] = ""
    discord: Optional[str] = ""
    photos: List[str] = []
    looking_for: List[str] = []
    premium: bool = False
    created_at: str
