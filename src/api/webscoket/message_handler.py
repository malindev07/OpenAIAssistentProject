from dataclasses import dataclass

from src.api.webscoket.models import (
    WebSocketTypes,
    WebsocketMessage,
    NotTypeResponse,
    UnknownTypeResponse,
    SipCallResponse,
    SipRegisterTypeResponse,
    PingTypeResponse,
    WebsocketResponse,
)


@dataclass
class MessageHandler:
    """Обработчик сообщений"""

    TYPES = ["ping", "sip_register", "sip_call"]

    async def get_response_by_type(
        self, msg_data: WebsocketMessage
    ) -> WebsocketResponse:

        if msg_data.type not in self.TYPES:
            res = await self._invalid_data()
            return WebsocketResponse(data=res.model_dump())

        if msg_data.type == WebSocketTypes.PING.value:
            res = await self._ping(msg_data)
        elif msg_data.type == WebSocketTypes.SIP_REGISTER.value:
            res = await self._sip_register(msg_data.client_id)
        elif msg_data.type == WebSocketTypes.SIP_CALL.value:
            res = await self._sip_call(msg_data.client_id)
        else:
            res = await self._unknown_type()

        return WebsocketResponse(data=res.model_dump())

    async def _ping(self, msg_data: WebsocketMessage) -> PingTypeResponse:
        return PingTypeResponse(timestamp=msg_data.timestamp)

    async def _sip_register(self, client_id: str) -> SipRegisterTypeResponse:
        return SipRegisterTypeResponse(client_id=client_id)

    async def _sip_call(self, client_id: str) -> SipCallResponse:
        return SipCallResponse(client_id=client_id)

    async def _unknown_type(self) -> UnknownTypeResponse:
        return UnknownTypeResponse()

    async def _invalid_data(self) -> NotTypeResponse:
        return NotTypeResponse()


message_handler = MessageHandler()
