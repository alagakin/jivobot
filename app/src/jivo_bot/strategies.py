from typing import List
import httpx
import uuid
from abc import ABC, abstractmethod
from jivo_bot.repository import AbstractRepository
from jivo_bot.schemas import JivoRequest, ChatMessageSchema
from config import JIVO_KEY, JIVO_URL
from loggers import logger


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

    async def get_history(self, client_id: str, chat_id: str, channel_id: str):
        data = {
            "client_id": client_id,
            "chat_id": chat_id,
            "channel_id": channel_id
        }
        return await self._repository.query(data)

    @staticmethod
    async def send(url, data):
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(url, json=data, headers=headers)
                status_code = response.status_code
                if status_code != 200:
                    logger.error(f"Request error: {response}; url: {url}; Data: {data}")
                return status_code

        except httpx.RequestError as err:
            logger.error(f"Request error: {err}")
            return None


class EchoStrategy(ResponseStrategy):
    async def send_response(self, request: JivoRequest):
        client_id = request.client_id
        chat_id = request.chat_id
        channel_id = request.channel.id
        received_text = request.message.text

        await self.save_request(client_id, chat_id, channel_id, received_text)
        history = await self.get_history(client_id, chat_id, channel_id)

        response_text = await self.generate_response(request, history)

        url = f"{JIVO_URL}/{JIVO_KEY}"
        data = {
            "id": str(uuid.uuid4()),
            "client_id": request.client_id,
            "chat_id": request.chat_id,
            "message": {
                "type": "TEXT",
                "text": response_text,
            },
            "event": "BOT_MESSAGE"
        }
        status_code = await self.send(url, data)

        if status_code == 200:
            await self.save_response(client_id, chat_id, channel_id, response_text)

    async def generate_response(self, request: JivoRequest, history: List[ChatMessageSchema]) -> str:
        return f"{request.message.text!r}\n Recorded messages - {len(history)}"


class OpenAIStrategy(ResponseStrategy, ABC):
    pass
