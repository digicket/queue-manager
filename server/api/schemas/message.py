from enum import Enum

from pydantic import BaseModel, constr


class MessageType(str, Enum):
    JSON: str = 'JSON'


class Metadata(BaseModel):
    type: MessageType


class Message(BaseModel):
    metadata: Metadata
    payload: constr(max_length=3200)  # Limit max message size


class ReturnMessage(BaseModel):
    message_id: str



