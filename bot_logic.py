import json
import re
import time
from amocrm_api import create_contact, create_lead, create_task_for_manager, get_contact_leads
from state_manager import load_state, save_state

# Загрузка сценария из JSON
with open("scenario.json", "r", encoding="utf-8") as f:
    scenario = json.load(f)

# Основная функция логики работы бота
def get_bot_response(phone: str, text: str) -> str:
    state = load_state()
    
    # Если клиента нет в состоянии, инициализируем его
    if phone not in state:
        state[phone] = {"step": 1, "name": "", "timestamp": ""}
        save_state(state)    
        return scenario["greeting"]
    
    # Получаем текущий этап клиента
    current_step = state[phone]["step"]

    # Этап 1: запрос имени
    if current_step == 1:
        state[phone] = {"step": 2, "name": text, "timestamp": ""}
        save_state(state)
        create_contact(text, phone)  # Создаем контакт в amoCRM
        return scenario["greet_reply"][0].format(name=text) + "\n".join(scenario["greet_reply"][1:])

    # Этап 2: выбор интереса
    elif current_step == 2:
        if text == "1":
            state[phone]["step"] = 3.1  # Переход на этап 3 по 1 варианту
            save_state(state)
            return scenario["greet_menu"]["1"]
        elif text == "2":
            state[phone]["step"] = 3.2  # Переход на этап 3 по 2 варианту
            save_state(state)
            return scenario["greet_menu"]["2"]
        else:
            return scenario["greet_menu"]["3"]
    
    # Этап 3.1: клиент выбрал конкретный аппарат
    elif current_step == 3.1:
        response = check_lazer(text)
        if response != scenario["lazer_helper"]:
            state[phone]["step"] = 4 # Переход на этап 4, если получил инфу по аппарату
            state[phone]["lead_id"] = create_lead(state[phone]["name"])  # Создаем сделку в amoCRM
            save_state(state)
        return response
    
    # Этап 3.2: клиент нуждается в помощи с подбором
    elif current_step == 3.2:
        state[phone]["step"] = 4 # Переход на этап 4
        state[phone]["lead_id"] = create_lead(state[phone]["name"])  # Создаем сделку в amoCRM
        save_state(state)
        entity_id = get_contact_leads(state[phone]["lead_id"])  # Получаем ID контакта
        create_task_for_manager(entity_id, "leads", f"Связаться с клиентом {state[phone]['name']} по телефону {phone}", deadline_hours=2)
        return scenario["manager_wait"]
    
    # Этап 4: ответы на FAQ
    elif current_step == 4:
        return check_faq(text)
    
    # Если клиент не отвечает в течение 24 часов - напоминание
    if is_inactive(state[phone]["last_timestamp"]) and current_step != 5:
        return scenario["no_answer"]
    
    # Этап 5: клиент просит больше не писать
    if text.lower() in ["стоп", "хватит", "не писать", "не звонить", "отписаться", "не пишите мне больше"]:
        state[phone]["step"] = 5
        save_state(state)
        return scenario["thanks"]
    # Если клиент написал после этапа 5, возвращаем его на этап 4
    if current_step == 5:
        state[phone]["step"] = 4
        save_state(state)
        return get_bot_response(phone, text) 

    return scenario["manager_faq"]     

# Проверка: прошло ли 24 часа после отправки сообщения клиенту
def is_inactive(last_timestamp: float) -> bool:
    now = time.time()
    return (now - last_timestamp) > 86400

# Функция для проверки ключевых слов FAQ и возврата ответа
def check_faq(user_text: str) -> str:
    user_text = user_text.lower()   # приводим текст к нижнему регистру

    # Поиск по ключевым словам
    if re.search(r"\bгарант\w*\b", user_text):
        return scenario["faq"]["гарантия"]
    
    if re.search(r"\bдостав\w*\b", user_text):
        return scenario["faq"]["доставка"]
    
    if re.search(r"\bоплат\w*\b", user_text):
        return scenario["faq"]["оплата"]

    if re.search(r"\bобучени\w*\b", user_text):
        return scenario["faq"]["обучение"]
    
    if re.search(r"\bпроизвод\w*\b", user_text):
        return scenario["faq"]["производитель"]
    
    if re.search(r"\bсоц\w*\b", user_text):
        return scenario["faq"]["соцконтракт"]

    if re.search(r"\bпрайс\w*\b", user_text):
        return scenario["faq"]["прайс"]
    
    if re.search(r"\bкомпани\w*\b", user_text):
        return scenario["faq"]["компания"]
   
    # Если ничего не найдено - передаем менеджеру
    return scenario["manager_faq"]

def check_lazer(user_text: str) -> str:
    if re.search(r"\bSkinStar Nd\b", user_text):
        return scenario["lazers"]["SkinStar Nd"]
    
    if re.search(r"\bNeoLaser Nd\b", user_text):
        return scenario["lazers"]["NeoLaser Nd"]
    
    if re.search(r"\bNeoLaser Titanium\b", user_text):
        return scenario["lazers"]["NeoLaser Titanium"]
    
    if re.search(r"\bSkinStar Diode\b", user_text):
        return scenario["lazers"]["SkinStar Diode"]
    
    if re.search(r"\bNeoLaser Diode\b", user_text):
        return scenario["lazers"]["NeoLaser Diode"]
    
    if re.search(r"\bNeoCryo\b", user_text):
        return scenario["lazers"]["NeoCryo"]
    
    #если нет - вызываем вспомогательное сообщение
    return scenario["lazer_helper"]
    