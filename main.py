from fastapi import FastAPI, Request
import requests
from models import Message
from storage import storage
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
    data = await request.json()  # получаем JSON от Wazzup
    logging.info(f"Получен вебхук: {data}")  # Логируем весь JSON
    phone = data["messages"][0]["chatId"]  
    text = data["messages"][0]["text"]
    
    message = Message(phone=phone, text=text)
    storage.append(message)

    answer_bot = get_bot_response(phone, text) 
    send_message(phone, answer_bot)  # Отправка ответа клиенту через Wazzup

    return {"status": "ok"}

#4 Получение всех сообщений
@app.get("/messages")
def get_messages():
    return {"messages": [msg.dict() for msg in storage]}

#5 Вебхук для amoCRM 
@app.post("/amocrm/callback")
async def send_to_amocrm(request: Request):
    data = await request.json()
    return {"status": "received", "data": data}


def send_message(phone: str, text: str):
    url = "https://api.wazzup24.com/v3/message"  # базовый URL API
    headers = {"Authorization": f"Bearer {WAZZUP_TOKEN}"}
    data = {
        "channelId": WAZZUP_CHANEL_ID,
        "chatType": "whatsapp",
        "chatId": phone,                 # номер клиента
        "text": text
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
