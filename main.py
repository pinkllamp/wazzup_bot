from fastapi import FastAPI, Request
import requests
from bot_logic import get_bot_response
from dotenv import load_dotenv
import os

#для тестов
import logging  
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = FastAPI()
WAZZUP_TOKEN = os.getenv("WAZZUP_TOKEN")
WAZZUP_CHANEL_ID = os.getenv("WAZZUP_CHANNEL_ID")

#1 Главная страница
@app.get("/")
async def home():
    return {"message": "Server is working!"}

#2 Проверка работоспособности сервера
@app.get("/health")
def health():
    return {"status": "ok"}

#3 Вебхук для Wazzup
@app.post("/wazzup/webhook")
async def wazzup_webhook(request: Request):
    try:
        data = await request.json()
        logging.info("Webhook payload: %s", data)

        messages = data.get("messages", [])
        if not messages:
            logging.warning("Нет сообщений в вебхуке")
            return {"status": "ok"}

        for msg in messages:
            phone = msg.get("chatId")
            text = msg.get("text", "")  

            answer_bot = get_bot_response(phone, text)
            logging.info("Ответ бота: %s", answer_bot)

            try:
                result = send_message(phone, answer_bot)
                logging.info("Wazzup ответил: %s", result)
            except Exception as e:
                logging.error("Ошибка при отправке сообщения через Wazzup: %s", e)

        return {"status": "ok"}

    except Exception as e:
        logging.exception("Ошибка в обработчике вебхука")
        return {"status": "error", "details": str(e)}

#4 Вебхук для amoCRM 
@app.post("/amocrm/callback")
async def send_to_amocrm(request: Request):
    data = await request.json()
    return {"status": "received", "data": data}

def send_message(phone: str, text: str):
    if not WAZZUP_TOKEN or not WAZZUP_CHANEL_ID:
        logging.error("Нет WAZZUP_TOKEN или WAZZUP_CHANEL_ID")
        return {"error": "missing config"}
    
    url = "https://api.wazzup24.com/v3/message"  # базовый URL API
    headers = {"Authorization": f"ApiKey {WAZZUP_TOKEN}"}
    data = {
        "channelId": WAZZUP_CHANEL_ID,
        "chatType": "whatsapp",
        "chatId": phone,                 # номер клиента
        "text": text
    }

    logging.info("Отправка сообщения в Wazzup: %s", data)

    try:
        response = requests.post(url, headers=headers, json=data)
        logging.info("Ответ Wazzup: %s %s", response.status_code, response.text)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Ошибка при отправке сообщения через Wazzup: %s", e)
        return {"error": str(e)}
