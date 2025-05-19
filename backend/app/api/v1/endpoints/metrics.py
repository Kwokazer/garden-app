# backend/app/api/v1/endpoints/metrics.py

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """
    Простой эндпоинт для Prometheus метрик
    В будущем здесь можно добавить настоящие метрики приложения
    """
    # Базовые метрики для начала
    metrics = [
        "# HELP garden_api_info Information about Garden API",
        "# TYPE garden_api_info gauge",
        "garden_api_info{version=\"0.1.0\"} 1",
        "",
        "# HELP garden_api_up Whether the API is up",
        "# TYPE garden_api_up gauge", 
        "garden_api_up 1",
        "",
    ]
    
    return "\n".join(metrics)