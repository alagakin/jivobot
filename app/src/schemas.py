from typing import Union

from pydantic import BaseModel


class Sender(BaseModel):
    id: int
    name: str = None
    url: str
    has_contacts: bool


class Message(BaseModel):
    type: str
    text: str = None
    timestamp: int


class Channel(BaseModel):
    id: str
    type: str


class JivoRequest(BaseModel):
    id: str
    site_id: int
    client_id: str
    chat_id: str
    agents_online: bool = None
    sender: Sender
    message: Message
    channel: Channel
    event: str
    options: Union[None, dict] = None


class ChatMessageSchema(BaseModel):
    id: int
    client_id: str
    chat_id: str
    channel_id: str
    from_bot: bool
    text: str

    class Config:
        from_attributes = True