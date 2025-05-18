import json
import datetime
from typing import Any

class CustomJSONEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер с поддержкой datetime"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)

def json_dumps(obj: Any) -> str:
    """Обертка для json.dumps с использованием кастомного энкодера"""
    return json.dumps(obj, cls=CustomJSONEncoder)

def json_loads(s: str) -> Any:
    """Обертка для json.loads"""
    return json.loads(s)