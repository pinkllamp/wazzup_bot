from fastapi import FastAPI, Request
import os
import asyncio
import logging  
from bot_logic import get_bot_response
from send_messages import send_message, reminder_worker

app = FastAPI()

# Для тестов
logging.basicConfig(level=logging.INFO)

# УДАЛИТЬ - очистка state.json при каждом рестарте сервера
import json
if os.path.exists("state.json"):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({}, f)

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
            if msg.get("isEcho", False):
                logging.info("Это эхо-сообщение, пропускаем обработку.")
                return {"status": "ok"}
        
            phone = msg.get("chatId")
            text = msg.get("text", "")  
            channel_id = msg.get("channelId")

            answer_bot = get_bot_response(phone, text)
            logging.info("Ответ бота: %s", answer_bot)

            try:
                result = send_message(phone, answer_bot, channel_id)
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

#5 Фоновая задача для напоминаний
@app.on_event("startup")
async def startup_event():
    """При старте сервера запускаем фоновую проверку"""
    asyncio.create_task(reminder_worker())

