from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from config import SECRET_KEY, ALGORITHM
from models.user import UserUpdate
from utils.storage import get_user, save_user, get_users
from utils.filters import get_swipe_candidates

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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
    
    # Проверяем заполнена ли регистрация
    is_completed = (
        user.get("gender") and 
        user.get("age") and 
        user.get("city") and 
        len(user.get("games", [])) > 0
    )
    
    # Помечаем как зарегистрированный
    if is_completed:
        user["is_registered"] = True
    
    save_user(user)
    return {"user": user}

@router.get("/users/swipe")
async def get_swipe_users(user=Depends(get_current_user)):
    # Проверяем что текущий пользователь зарегистрирован
    if not user.get("is_registered", False):
        return {"users": []}
    
    all_users = get_users()
    
    # Фильтруем: только зарегистрированные пользователи
    registered_users = {
        uid: u for uid, u in all_users.items()
        if u.get("is_registered", False)
    }
    
    candidates = get_swipe_candidates(user, registered_users)
    hidden = ["likes_today", "last_like_reset", "viewed_profiles", "is_registered"]
    safe = [{k: v for k, v in c.items() if k not in hidden} for c in candidates]
    return {"users": safe}