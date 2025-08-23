import requests
import time
from tokens_manager import get_access_token, AMO_BASE

def create_contact(name: str, phone: str):
    url = f"{AMO_BASE}/api/v4/contacts"
    headers = {"Authorization": f"Bearer {get_access_token()}"}
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

def create_lead(name: str, model : str):
    url = f"{AMO_BASE}/api/v4/leads"
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    data = [{"name": name, "model": model}]
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    lead = response.json()["_embedded"]["leads"][0]
    return lead["id"]  # возвращаем ID сделки

def create_task_for_manager(entity_id: int, entity_type: str, text: str, responsible_user_id: int = None, deadline_hours: int = 24):
    """
    Создаёт задачу менеджеру в amoCRM.
    :param entity_id: ID сделки или контакта
    :param entity_type: "leads", "contacts" или "companies"
    :param text: текст задачи
    :param deadline_hours: через сколько часов выполнить задачу
    """
    url = f"{AMO_BASE}/api/v4/tasks"
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    
    complete_till = int(time.time()) + deadline_hours * 3600  # дедлайн через N часов

    data = [{
        "entity_id": entity_id,
        "entity_type": entity_type,
        "text": text,
        "complete_till": complete_till
    }]

    if responsible_user_id:
        data[0]["responsible_user_id"] = responsible_user_id

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def get_contact_leads(contact_id: int):
    url = f"{AMO_BASE}/api/v4/contacts/{contact_id}?with=leads"
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["_embedded"]["leads"]