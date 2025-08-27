import requests
import time
import json
import asyncio
import logging
import os
from dotenv import load_dotenv
from state_manager import load_state, save_state

# Загрузка переменных окружения
load_dotenv()
WAZZUP_TOKEN = os.getenv("WAZZUP_TOKEN")

# --- Функция отправки сообщений через Wazzup ---
def send_message(phone: str, text: str, channel_id: str):
    url = "https://api.wazzup24.com/v3/message" 
    headers = {
        "Authorization": f"Bearer {WAZZUP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "channelId": channel_id,
        "chatType": "whatsapp",
        "chatId": phone,         
        "text": text
    }
    
    logging.info("Хедеры запроса: %s", headers)
    logging.info("Отправка сообщения в Wazzup: %s", data)

    try:
        response = requests.post(url, headers=headers, json=data)
        logging.info("Ответ Wazzup: %s %s", response.status_code, response.text)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Ошибка при отправке сообщения через Wazzup: %s", e)
        return {"error": str(e)}


# --- Фоновая задача для напоминаний ---
REMINDER_DELAY = 24 * 60 * 60  # 24 часа = 86400 секунд
with open("scenario.json", "r", encoding="utf-8") as f:
    scenario = json.load(f)

async def reminder_worker():
    """Каждый час проверяем, не пора ли напомнить клиентам"""
    while True:
        try:
            state = load_state()
            now = time.time()
            updated = False

            for phone, info in state.items():
                last_ts = info.get("timestamp", 0)
                do_not_disturb = info.get("step")
                channel_id = info.get("channelId")

                if do_not_disturb!=5 and now - last_ts > REMINDER_DELAY:
                    logging.info(f"Отправляем напоминание клиенту {phone}")
                    send_message(phone, scenario["no_answer"], channel_id)
                    state[phone]["timestamp"] = now  # обновляем время
                    updated = True

            if updated:
                save_state(state)

        except Exception as e:
            logging.error("Ошибка в reminder_worker: %s", e)

        await asyncio.sleep(3600)  # ждём 1 час



