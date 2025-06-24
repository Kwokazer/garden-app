from fastapi import APIRouter

try:
    from app.api.v1.endpoints import auth, users, plants, climate_zones, questions, answers, tags, plant_categories, webinars, file_upload
except ImportError:
    # Обработка случая, когда некоторые эндпоинты еще не созданы
    from app.api.v1.endpoints import auth, users, plants, climate_zones, questions, answers, tags, plant_categories, webinars, file_upload

api_router = APIRouter()

# Корневой эндпоинт API v1
@api_router.get("/")
async def api_root():
    """
    Корневой эндпоинт API v1
    """
    return {
        "message": "Garden API v1",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "plants": "/plants",
            "plant_categories": "/plant-categories",
            "climate_zones": "/climate-zones",
            "questions": "/questions",
            "answers": "/answers",
            "tags": "/tags",
            "webinars": "/webinars",
            "file_upload": "/files",
        }
    }

# Регистрация эндпоинтов
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(plants.router, prefix="/plants", tags=["plants"])
api_router.include_router(plant_categories.router, prefix="/plant-categories", tags=["plant_categories"])
api_router.include_router(climate_zones.router, prefix="/climate-zones", tags=["climate_zones"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(answers.router, prefix="/answers", tags=["answers"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(webinars.router, prefix="/webinars", tags=["webinars"])
api_router.include_router(file_upload.router, prefix="/files", tags=["file_upload"])