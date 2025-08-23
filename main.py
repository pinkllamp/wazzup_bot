from fastapi import FastAPI, Request
import requests
from models import Message
from storage import storage
from tokens_manager import get_access_token
from message import get_bot_response

app = FastAPI()

WAZZUP_TOKEN = "138c161ae2094e279cab054f2d4c9972"
CHANNEL_ID = "79278605959"
AMO_BASE= "https://isasvetlana.amocrm.ru"

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
   
    phone = data.get("phone")
    text = data.get("text")
    
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
    print("Webhook от amoCRM:", data)
    return {"status": "received"}


def send_message(phone: str, text: str):
    url = "https://api.wazzup24.com/v3/message"  # базовый URL API
    headers = {"Authorization": f"Bearer {WAZZUP_TOKEN}"}
    data = {
        "channelId": "your_channel_id",  # ID канала из Wazzup
        "chatType": "whatsapp",
        "chatId": phone,                 # номер клиента
        "text": text
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
