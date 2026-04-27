from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from utils.storage import get_user, get_user_matches

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

@router.get("/matches")
async def get_matches(user=Depends(get_current_user)):
    """Получить мэтчи текущего пользователя"""
    user_matches = get_user_matches(user["telegram_id"])
    
    result = []
    for m in user_matches:
        partner = get_user(m["partner_id"])
        if partner:
            # Скрываем критичные данные
            hidden = [
                "likes_today",
                "last_like_reset",
                "viewed_profiles",
                "is_registered"
            ]
            safe = {k: v for k, v in partner.items() if k not in hidden}
            result.append({
                "user": safe,
                "created_at": m["created_at"]
            })
    
    return {"matches": result}