from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from config import SECRET_KEY, ALGORITHM, FREE_LIKES_PER_DAY
from models.like import LikeCreate, LikeSkip
from utils.storage import (
    get_user, save_user, add_like, has_liked,
    add_match, match_exists
)
from utils.notifications import notify_match

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        telegram_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def reset_likes_if_needed(user: dict) -> dict:
    today = str(datetime.now().date())
    if user.get("last_like_reset") != today:
        user["likes_today"] = 0
        user["last_like_reset"] = today
    return user


@router.post("/swipe/like")
async def like_user(body: LikeCreate, user=Depends(get_current_user)):
    user = reset_likes_if_needed(user)

    if not user.get("premium", False) and user.get("likes_today", 0) >= FREE_LIKES_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily like limit reached")

    to_user_data = get_user(body.to_user)
    if not to_user_data:
        raise HTTPException(status_code=404, detail="User not found")

    my_id = user["telegram_id"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Добавляем лайк если ещё не лайкали
    if not has_liked(my_id, body.to_user):
        add_like(my_id, body.to_user, now)
        user["likes_today"] = user.get("likes_today", 0) + 1

    # Добавляем в просмотренные
    viewed = user.get("viewed_profiles", [])
    if body.to_user not in viewed:
        viewed.append(body.to_user)
        user["viewed_profiles"] = viewed

    save_user(user)

    # Проверяем матч
    they_liked_me = has_liked(body.to_user, my_id)
    is_new_match = False
    match_user = None

    if they_liked_me and not match_exists(my_id, body.to_user):
        add_match(my_id, body.to_user, now)
        is_new_match = True

        hidden = ["likes_today", "last_like_reset", "viewed_profiles"]
        match_user = {
            k: v for k, v in to_user_data.items()
            if k not in hidden
        }

        try:
            notify_match(user, to_user_data)
        except Exception as e:
            print(f"[NOTIFY] Error: {e}")

    remaining = (
        max(0, FREE_LIKES_PER_DAY - user.get("likes_today", 0))
        if not user.get("premium") else -1
    )

    return {
        "match": is_new_match,
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