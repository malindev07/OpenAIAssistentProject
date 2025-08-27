import json
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from src.api.webscoket.connection_manager import manager
from src.api.webscoket.message_handler import message_handler
from src.api.webscoket.models import WebsocketMessage, ErrorDataResponse
from src.domain.logger.logger import get_logger

ws_router = APIRouter()

KEYS = ["type", "timestamp"]

logger = get_logger(__name__)


@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """ "Вебсокет эндпоинт, вход websocket  и client_id"""
    await manager.connect(websocket=websocket, client_id=client_id)

    try:
        logger.info(f"{client_id} connected")
        while True:
            data = await websocket.receive_text()

            message_data = json.loads(data)

            # Проверяем все ли нужные данные есть в сообщении
            if all(k in message_data for k in KEYS):
                msg = WebsocketMessage(
                    type=message_data["type"],
                    client_id=client_id,
                    timestamp=str(message_data["timestamp"]),
                )

                response = await message_handler.get_response_by_type(msg_data=msg)
                await manager.send_json(response.data, client_id)
            else:
                response = ErrorDataResponse()
                await manager.send_json(response.model_dump(), client_id)
    # Ловим исключение, если соединение прерывается
    except WebSocketDisconnect:
        await manager.disconnect(client_id=client_id)
