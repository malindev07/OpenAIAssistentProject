from fastapi import APIRouter, Response, Request

from src.api.health.schema import HealthServiceSchema, HealthVoiceKitSchema

health_router = APIRouter(prefix="/health", tags=["Health Check"])


@health_router.get("")
async def get_health(request: Request) -> HealthServiceSchema:
    """Проверка доступности сервиса"""
    return HealthServiceSchema(version=request.app.version)


@health_router.get("/ready")
async def get_health_voicekit(request: Request) -> HealthVoiceKitSchema:
    """Проверка доступности сервиса voicekit (Т-банк) пока заглушка
    Если соединение установлено
        :return HealthVoiceKitSchema(ready=True, voicekit_status="connected")
    если не установлено:
        :return HealthVoiceKitSchema(ready=False, voicekit_status="error")
    """
    return HealthVoiceKitSchema(ready=True, voicekit_status="connected")
