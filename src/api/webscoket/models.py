from enum import Enum

from pydantic import BaseModel, Field


class WebSocketTypes(Enum):
    PING = "ping"
    SIP_REGISTER = "sip_register"
    SIP_CALL = "sip_call"


class WebsocketMessage(BaseModel):
    type: str
    client_id: str
    timestamp: str


class PingTypeResponse(BaseModel):
    type: str = Field(default="pong")
    timestamp: str


class SipRegisterTypeResponse(BaseModel):
    status: str = Field(default="ok")
    registration: str = Field(default="successful")
    client_id: str


class SipCallResponse(BaseModel):
    status: str = Field(default="ok")
    client_id: str


class UnknownTypeResponse(BaseModel):
    error: str = Field(default="error")
    error_msg: str = Field(default="Invalid type")


class NotTypeResponse(BaseModel):
    error: str = Field(default="error")
    error_msg: str = Field(default="Invalid data, not type in json")


class ErrorDataResponse(BaseModel):
    error: str = Field(default="error")
    error_msg: str = Field(default="Invalid data")


class WebsocketResponse(BaseModel):
    data: dict[str, str]
