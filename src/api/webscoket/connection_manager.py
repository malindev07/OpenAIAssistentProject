from dataclasses import dataclass, field

from fastapi import WebSocket


@dataclass
class ConnectionManager:

    active_connections: dict[str, WebSocket] = field(default_factory=dict)

    async def connect(self, websocket: WebSocket, client_id: str):
        """Соединение и сохранение сокета в словарь"""

        if client_id not in self.active_connections:
            await websocket.accept()
            self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str):
        """Отклбчение сокета и удаление из словаря"""
        del self.active_connections[client_id]

    async def send_json(self, message: dict[str, str], client_id: str):
        """отправка json клиенту"""
        await self.active_connections[client_id].send_json(message)


manager = ConnectionManager()
