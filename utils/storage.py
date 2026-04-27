import json
import os
from config import USERS_FILE, LIKES_FILE, MATCHES_FILE, DATA_DIR

def _ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for f in [USERS_FILE, LIKES_FILE, MATCHES_FILE]:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as fp:
                json.dump({}, fp)

def _read(path: str) -> dict:
    _ensure_files()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write(path: str, data: dict):
    _ensure_files()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_users() -> dict:
    return _read(USERS_FILE)

def save_users(data: dict):
    _write(USERS_FILE, data)

def get_user(telegram_id: int):
    users = get_users()
    return users.get(str(telegram_id))

def save_user(user: dict):
    users = get_users()
    users[str(user["telegram_id"])] = user
    save_users(users)

def get_likes() -> dict:
    return _read(LIKES_FILE)

def save_likes(data: dict):
    _write(LIKES_FILE, data)

def add_like(from_user: int, to_user: int, created_at: str) -> str:
    likes = get_likes()
    like_id = str(len(likes) + 1)
    likes[like_id] = {"from_user": from_user, "to_user": to_user, "created_at": created_at}
    save_likes(likes)
    return like_id

def has_liked(from_user: int, to_user: int) -> bool:
    likes = get_likes()
    for like in likes.values():
        if like["from_user"] == from_user and like["to_user"] == to_user:
            return True
    return False

def get_matches() -> dict:
    return _read(MATCHES_FILE)

def save_matches(data: dict):
    _write(MATCHES_FILE, data)

def add_match(user1: int, user2: int, created_at: str) -> str:
    matches = get_matches()
    match_id = str(len(matches) + 1)
    matches[match_id] = {"user1": user1, "user2": user2, "created_at": created_at}
    save_matches(matches)
    return match_id

def match_exists(user1: int, user2: int) -> bool:
    matches = get_matches()
    for m in matches.values():
        pair = {m["user1"], m["user2"]}
        if pair == {user1, user2}:
            return True
    return False

def get_user_matches(telegram_id: int) -> list:
    matches = get_matches()
    result = []
    for m in matches.values():
        if m["user1"] == telegram_id or m["user2"] == telegram_id:
            partner_id = m["user2"] if m["user1"] == telegram_id else m["user1"]
            result.append({"partner_id": partner_id, "created_at": m["created_at"]})
    return result
