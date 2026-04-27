from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from models.user import UserUpdate
from utils.storage import get_user, save_user, get_users
from utils.filters import get_swipe_candidates

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        telegram_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/me")
async def get_me(user=Depends(get_current_user)):
    return {"user": user}

@router.patch("/users/me")
async def update_me(body: UserUpdate, user=Depends(get_current_user)):
    update_data = body.model_dump(exclude_none=True)
    user.update(update_data)
    save_user(user)
    return {"user": user}

@router.get("/users/swipe")
async def get_swipe_users(user=Depends(get_current_user)):
    all_users = get_users()
    candidates = get_swipe_candidates(user, all_users)
    hidden = ["likes_today", "last_like_reset", "viewed_profiles"]
    safe = [{k: v for k, v in c.items() if k not in hidden} for c in candidates]
    return {"users": safe}
