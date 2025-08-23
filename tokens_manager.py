import requests
import json
import time
from pathlib import Path

# Путь к файлу, где будут храниться токены
TOKENS_FILE = Path("tokens.json")
AMO_BASE = "https://isasvetlana.amocrm.ru" 

# Загружаем токены из файла
def load_tokens() -> dict:
    if TOKENS_FILE.exists():
        with TOKENS_FILE.open() as f:
            return json.load(f)
    return None

# Сохраняем токены в файл и добавляет время их истечения.
def save_tokens(tokens: dict):
    tokens["expires_at"] = int(time.time()) + tokens["expires_in"]
    with TOKENS_FILE.open("w") as f:
        json.dump(tokens, f)

# Обновляем токены через refresh_token
def refresh_tokens() -> dict:
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        raise RuntimeError("Нет refresh_token — пройди авторизацию заново.")
    
    url = f"{AMO_BASE}/oauth2/access_token"
    payload = {
        "client_id": "908fd6e9-f0f8-4d02-875f-ab6b7ba3a116", 
        "client_secret": "wuqiJNO1w7ReyaBIkEtcKIVm60fMAZuSJMZo4d67XY8aR2dpdZ9TM4ggXcMTNp7m", 
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "redirect_uri": "https://wazzup-bot.onrender.com/amocrm/callback"  
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    new_tokens = response.json()
    save_tokens(new_tokens)  # Сохраняем новые токены
    return new_tokens

# Получаем актуальный access_token
def get_access_token() -> str:
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("Нет токенов — сначала обменяй code на токены")
    
    # Если токен истёк — обновляем его
    if int(time.time()) > tokens.get("expires_at", 0) - 60:
        tokens = refresh_tokens()
    
    return tokens["access_token"]
