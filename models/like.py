from pydantic import BaseModel

class LikeCreate(BaseModel):
    to_user: int

class LikeSkip(BaseModel):
    to_user: int
