# AI Assistant Service

Ассистент на основе ИИ для повышение эффективности общения менеджерского состава с клиентами.
Расшифровка голоса с помощью сервиса VoiceKit от Т-Банка  

## API Endpoints
		GET /health - Health check

		GET /health/ready - Health check VoiceKit
    
## Выполненные этапы
	1) Реализованы эндпоинты для проверки дотсупности сервиса
	2) Настроено логгирование
	3) Добавлен Dockerfile для сборки
  
## Сборка проекта
	#Сборка образа
	1) docker build -t ai-assistant .
	#Создание и запуск контейнера
	2) docker run -p 8000:8000 ai-assistant

## Технологии
	Python 3.12 - Базовый язык
	FastAPI - Web framework
	Uvicorn - ASGI сервер
	Pydantic - Валидация данных
	Docker - Контейнеризация