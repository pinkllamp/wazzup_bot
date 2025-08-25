import json
import os
import time
from typing import Dict

STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}  # файла нет → возвращаем пустой dict

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:   # файл пустой
                return {}
            return json.loads(content)
    except Exception as e:
        # если файл повреждён → тоже возвращаем пустой dict
        print(f"Ошибка при чтении {STATE_FILE}: {e}")
        return {}

# Сохранение состояния клиента в файл
def save_state(state: Dict):
    state["timestamp"] = time()
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)