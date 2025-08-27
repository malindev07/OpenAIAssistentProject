# AI Assistant Service

Ассистент на основе ИИ для повышение эффективности общения менеджерского состава с клиентами.
Расшифровка голоса с помощью сервиса VoiceKit от Т-Банка  

## API Endpoints
		GET /health - Health check

		GET /health/ready - Health check VoiceKit
        
            ws://localhost:8000/ws/{client_id}
## Responses
1) GET /health
```json
{"status":"ok","service":"transcribation","version":"1.0.0"}
```
2) GET /health/ready 
```json
{"ready":true,"voicekit_status":"connected"}
```
3) ws://localhost:8000/ws/{client_id} 
```json
{"status":"ok","client_id":"test-client1"}
```
## Выполненные этапы
	1) Реализованы эндпоинты для проверки дотсупности сервиса
	2) Настроено логгирование
	3) Добавлен Dockerfile для сборки
    4) Добавлены Websockets
  
## Сборка проекта
	#Сборка образа
	1) docker build -t ai-assistant-websockets .
	#Создание и запуск контейнера
	2) docker run -p 8000:8000 --name ai-con-ws ai-assistant-websockets

## Технологии
	Python 3.12 - Базовый язык
	FastAPI - Web framework
	Uvicorn - ASGI сервер
	Pydantic - Валидация данных
	Docker - Контейнеризация
    Websockets - Постоянное соединение сервера и клиента