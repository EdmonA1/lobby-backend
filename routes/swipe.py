from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from config import SECRET_KEY, ALGORITHM, FREE_LIKES_PER_DAY
from models.like import LikeCreate, LikeSkip
from utils.storage import (
    get_user, save_user, add_like, has_liked, 
    add_match, match_exists, get_user_matches
)
from utils.notifications import notify_match

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

def reset_likes_if_needed(user):
    today = str(datetime.now().date())
    if user.get("last_like_reset") != today:
        user["likes_today"] = 0
        user["last_like_reset"] = today
    return user

@router.post("/swipe/like")
async def like_user(body: LikeCreate, user=Depends(get_current_user)):
    user = reset_likes_if_needed(user)
    
    # Проверяем лимит лайков
    if not user.get("premium", False) and user["likes_today"] >= FREE_LIKES_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily like limit reached")
    
    to_user_data = get_user(body.to_user)
    if not to_user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем что это не лайк самого себя
    if user["telegram_id"] == body.to_user:
        raise HTTPException(status_code=400, detail="Cannot like yourself")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Добавляем лайк если его ещё нет
    if not has_liked(user["telegram_id"], body.to_user):
        add_like(user["telegram_id"], body.to_user, now)
        user["likes_today"] = user.get("likes_today", 0) + 1
    
    # Добавляем в просмотренные
    viewed = user.get("viewed_profiles", [])
    if body.to_user not in viewed:
        viewed.append(body.to_user)
        user["viewed_profiles"] = viewed
    
    save_user(user)
    
    # Проверяем: лайкнул ли нас целевой пользователь?
    mutual_like = has_liked(body.to_user, user["telegram_id"])
    match_user = None
    
    if mutual_like:
        # Проверяем что мэтча ещё нет
        if not match_exists(user["telegram_id"], body.to_user):
            # Создаём новый мэтч
            add_match(user["telegram_id"], body.to_user, now)
            
            # Скрываем критичные данные
            hidden = ["likes_today", "last_like_reset", "viewed_profiles", "is_registered"]
            match_user = {k: v for k, v in to_user_data.items() if k not in hidden}
            
            # Отправляем уведомления обоим
            try:
                notify_match(user, to_user_data)
            except Exception as e:
                print(f"[NOTIFY ERROR] {e}")
    
    # Считаем оставшиеся лайки
    remaining = (
        -1 if user.get("premium") 
        else max(0, FREE_LIKES_PER_DAY - user["likes_today"])
    )
    
    return {
        "match": mutual_like,
        "match_user": match_user,
        "likes_remaining": remaining
    }

@router.post("/swipe/skip")
async def skip_user(body: LikeSkip, user=Depends(get_current_user)):
    viewed = user.get("viewed_profiles", [])
    if body.to_user not in viewed:
        viewed.append(body.to_user)
        user["viewed_profiles"] = viewed
    save_user(user)
    return {"success": True}