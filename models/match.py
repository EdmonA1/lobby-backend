from pydantic import BaseModel

class Match(BaseModel):
    user1: int
    user2: int
    created_at: str
