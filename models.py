from pydantic import BaseModel  # описание структуры сообщений

# Модель сообщения (структура данных)
class Message(BaseModel):
    phone: str
    text: str
