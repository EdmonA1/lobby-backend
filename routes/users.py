from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from utils.storage import get_user, save_user, get_users

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        telegram_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def is_profile_complete(user: dict) -> bool:
    """✅ Единая проверка завершённости профиля"""
    return bool(
        user.get("gender") and
        user.get("city") and
        user.get("age", 0) > 0 and
        user.get("name") and
        user.get("games") and len(user.get("games", [])) > 0
    )

@router.get("/users/me")
async def get_me(user=Depends(get_current_user)):
    return {
        "user": user,
        "profile_complete": is_profile_complete(user)
    }

@router.patch("/users/me")
async def update_me(body: dict, user=Depends(get_current_user)):
    # Разрешённые поля для обновления
    allowed = [
        "name", "age", "gender", "city", "games", "bio",
        "discord", "photos", "looking_for", "filter_gender",
        "filter_age_min", "filter_age_max"
    ]
    for key in allowed:
        if key in body:
            user[key] = body[key]

    # ✅ Обновляем флаг завершённости
    user["profile_complete"] = is_profile_complete(user)
    save_user(user)

    return {
        "user": user,
        "profile_complete": user["profile_complete"]
    }

@router.get("/users/swipe")
async def get_swipe_users(user=Depends(get_current_user)):
    # ✅ Проверяем что сам пользователь заполнил профиль
    if not is_profile_complete(user):
        raise HTTPException(
            status_code=403,
            detail="Complete your profile first"
        )

    all_users = get_users()
    viewed = set(user.get("viewed_profiles", []))
    my_id = user["telegram_id"]

    result = []
    for uid, u in all_users.items():
        if int(uid) == my_id:
            continue

        # ✅ ИСПРАВЛЕНИЕ: Показываем только заполненные анкеты
        if not is_profile_complete(u):
            continue

        if int(uid) in viewed:
            continue

        # Фильтр по полу
        filter_gender = user.get("filter_gender", "any")
        if filter_gender != "any" and u.get("gender") != filter_gender:
            continue

        # Фильтр по возрасту
        age = u.get("age", 0)
        if age < user.get("filter_age_min", 18):
            continue
        if age > user.get("filter_age_max", 60):
            continue

        # Скрываем приватные поля
        hidden = ["likes_today", "last_like_reset", "viewed_profiles"]
        clean = {k: v for k, v in u.items() if k not in hidden}
        result.append(clean)

    return {"users": result, "count": len(result)}