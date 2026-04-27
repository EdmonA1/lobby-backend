import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl
from config import BOT_TOKEN

def validate_telegram_data(init_data: str):
    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return None
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None
        user_str = parsed.get("user", "{}")
        user_data = json.loads(unquote(user_str))
        return user_data
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return None

def extract_user_from_init_data(init_data: str):
    return validate_telegram_data(init_data)
