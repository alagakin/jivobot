import json
from typing import List

import requests
from abc import ABC, abstractmethod

from jivo_bot.repository import AbstractRepository
from jivo_bot.schemas import JivoRequest, ChatMessageSchema
from config import JIVO_KEY, JIVO_URL


class ResponseStrategy(ABC):
    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    @abstractmethod
    async def send_response(self, request: JivoRequest):
        pass

    @abstractmethod
    async def generate_response(self, request: JivoRequest, history: List[ChatMessageSchema]):
        pass

    async def save_request(self, client_id: str, chat_id: str, channel_id: str, message: str):
        return await self.save(client_id, chat_id, channel_id, message, False)

    async def save_response(self, client_id: str, chat_id: str, channel_id: str, message: str):
        return await self.save(client_id, chat_id, channel_id, message, True)

    async def save(self, client_id: str, chat_id: str, channel_id: str, message: str, from_bot: bool):
        return await self._repository.add_one(
            {
                'client_id': client_id,
                'chat_id': chat_id,
                'channel_id': channel_id,
                "from_bot": from_bot,
                "text": message
            })

    async def get_history(self, **kwargs):
        return await self._repository.query(kwargs)


class EchoStrategy(ResponseStrategy):
    async def send_response(self, request: JivoRequest):
        await self.save_request(request.client_id, request.chat_id, request.channel.id, request.message.text)
        history = await self.get_history(client_id=request.client_id, chat_id=request.chat_id,
                                         channel_id=request.channel.id)
        response = await self.generate_response(request, history)
        data = {
            "id": request.id,
            "client_id": request.client_id,
            "chat_id": request.chat_id,
            "message": {
                "type": "TEXT",
                "text": response,
            },
            "event": "BOT_MESSAGE"
        }
        url = f"{JIVO_URL}/{JIVO_KEY}"
        json_data = json.dumps(data)
        # todo: check if message is sent
        requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
        await self.save_response(request.client_id, request.chat_id, request.channel.id, response)

    async def generate_response(self, request: JivoRequest, history: List[ChatMessageSchema]) -> str:
        return f"{request.message.text!r}\n Recorded messages - {len(history)}"


class OpenAIStrategy(ResponseStrategy, ABC):
    pass
