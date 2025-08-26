import requests
import time
from dotenv import load_dotenv
import os

AMO_BASE = os.getenv("AMO_BASE")
AMO_ACCESS_TOKEN = os.getenv("AMO_ACCESS_TOKEN")

def create_contact(name: str, phone: str):
    url = f"{AMO_BASE}/api/v4/contacts"
    headers = {"Authorization": f"Bearer {AMO_ACCESS_TOKEN}"}
    data = [{
        "name": name,
        "custom_fields_values": [
            {
                "field_code": "PHONE",
                "values": [{"value": phone}]
            }
        ]
    }]
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def create_lead(name: str):
    url = f"{AMO_BASE}/api/v4/leads"
    headers = {"Authorization": f"Bearer {AMO_ACCESS_TOKEN}"}
    data = [{"name": name}]
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    lead = response.json()["_embedded"]["leads"][0]
    return lead["id"]  # возвращаем ID сделки

def create_task_for_manager(entity_id: int, entity_type: str, text: str, deadline_hours: int = 24):
    """
    Создаёт задачу менеджеру в amoCRM.
    entity_id: ID сделки или контакта
    entity_type: "leads", "contacts" или "companies"
    text: текст задачи
    deadline_hours: через сколько часов выполнить задачу
    """
    url = f"{AMO_BASE}/api/v4/tasks"
    headers = {"Authorization": f"Bearer {AMO_ACCESS_TOKEN}"}
    
    complete_till = int(time.time()) + deadline_hours * 3600  # дедлайн 

    data = [{
        "entity_id": entity_id,
        "entity_type": entity_type,
        "text": text,
        "complete_till": complete_till
    }]

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def get_contact_leads(contact_id: int):
    url = f"{AMO_BASE}/api/v4/contacts/{contact_id}?with=leads"
    headers = {
        "Authorization": f"Bearer {AMO_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    
    # Проверим на случай пустого ответа
    if response.status_code == 204 or not response.text.strip():
        return []
    
    response.raise_for_status()
    data = response.json()
    
    return data.get("_embedded", {}).get("leads", [])