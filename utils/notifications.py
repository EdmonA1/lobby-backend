import httpx
import asyncio
import json
from config import BOT_TOKEN

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_match_notification(user1: dict, user2: dict):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            for user, partner in [(user1, user2), (user2, user1)]:
                partner_name = partner.get("name", "Игрок")
                partner_username = partner.get("username", "")
                partner_link = f"@{partner_username}" if partner_username else partner_name
                text = (
                    f"🎮 <b>У вас мэтч!</b>\n\n"
                    f"Вы и {partner_name} понравились друг другу!\n"
                    f"Напишите первым: {partner_link}"
                )
                payload = {
                    "chat_id": user["telegram_id"],
                    "text": text,
                    "parse_mode": "HTML"
                }
                if partner_username:
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": "💬 Написать", "url": f"https://t.me/{partner_username}"}
                        ]]
                    }
                    payload["reply_markup"] = json.dumps(keyboard)
                await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
    except Exception as e:
        print(f"[NOTIFY ERROR] {e}")

def notify_match(user1: dict, user2: dict):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(send_match_notification(user1, user2))
        else:
            loop.run_until_complete(send_match_notification(user1, user2))
    except Exception as e:
        print(f"[NOTIFY SYNC ERROR] {e}")
