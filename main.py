from fastapi import FastAPI, Request
import requests

app = FastAPI()

WAZZUP_TOKEN = "138c161ae2094e279cab054f2d4c9972"
CHANNEL_ID = "79278605959"

@app.get("/")
async def home():
    return {"message": "Server is working!"}

def reply_to_client(phone: str, text: str):
    url = "https://api.wazzup24.com/v3/message"
    headers = {
        "Authorization": f"Bearer {WAZZUP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channelId": CHANNEL_ID,
        "chatType": "whatsapp",
        "phone": phone,
        "text": text
    }
    response = requests.post(url, headers=headers, json=payload)    #отправляем POST-запрос в формате JSON
    print("Ответ отправлен:", response.status_code, response.text)

@app.post("/wazzup/webhook")
async def wazzup_webhook(request: Request):
    data = await request.json()  # получаем JSON от Wazzup
    print("Пришло сообщение:", data)
   
    phone = data["messages"][0]["from"]
    text = data["messages"][0]["text"]

    reply_to_client(phone, "Спасибо! Мы получили ваше сообщение.")

    return {"status": "ok"}
