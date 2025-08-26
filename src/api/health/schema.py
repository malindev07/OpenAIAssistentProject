from pydantic import BaseModel, Field


class HealthServiceSchema(BaseModel):
    status: str = Field(default="ok")
    service: str = Field(default="transcribation")
    version: str


class HealthVoiceKitSchema(BaseModel):
    ready: bool
    voicekit_status: str
