import json
import os
import time
from typing import Dict

# Загрузка состояния из файла
def load_state() -> Dict:
    if os.path.exists("state.json"):
        with open("state.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
# Сохранение состояния клиента в файл
def save_state(state: Dict):
    state["timestamp"] = time()
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)