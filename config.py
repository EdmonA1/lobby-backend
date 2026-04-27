import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SECRET_KEY     = os.getenv("SECRET_KEY", "changeme-please-set-in-env")
BOT_TOKEN      = os.getenv("BOT_TOKEN", "")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8080,http://127.0.0.1:8080"
).split(",")
ALGORITHM               = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE  = os.path.join(DATA_DIR, "users.json")
LIKES_FILE  = os.path.join(DATA_DIR, "likes.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")
FREE_LIKES_PER_DAY = 10
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"