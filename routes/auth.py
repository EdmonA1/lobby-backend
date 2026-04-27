from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS
from utils.telegram_auth import extract_user_from_init_data
from utils.storage import get_user, save_user
import os

router = APIRouter()

class AuthRequest(BaseModel):
    initData: str

def create_token(telegram_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(telegram_id), "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

@router.post("/auth/telegram")
async def auth_telegram(body: AuthRequest):
    tg_user = None

    # Режим разработки — принимаем mock данные
    if DEV_MODE and body.initData in ("mock_init_data_for_development", ""):
        tg_user = {
            "id": 123456789,
            "first_name": "Dev",
            "username": "devuser"
        }
        print("[AUTH] DEV MODE: using mock user")
    else:
        tg_user = extract_user_from_init_data(body.initData)

    if not tg_user:
        raise HTTPException(status_code=401, detail="Invalid Telegram data")

    telegram_id = tg_user.get("id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="No user id in data")

    existing = get_user(telegram_id)
    token = create_token(telegram_id)

    if existing:
        return {"user": existing, "token": token, "registered": True}

    new_user = {
        "telegram_id": telegram_id,
        "username": tg_user.get("username", ""),
        "name": tg_user.get("first_name", "Игрок"),
        "age": 18,
        "gender": "",
        "city": "",
        "games": [],
        "bio": "",
        "discord": "",
        "photos": [],
        "looking_for": [],
        "filter_gender": "any",
        "filter_age_min": 18,
        "filter_age_max": 60,
        "premium": False,
        "likes_today": 0,
        "last_like_reset": str(datetime.now().date()),
        "viewed_profiles": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_user(new_user)
    return {"user": new_user, "token": token, "registered": False}