import json
import random
from typing import List, Union
import httpx
import uuid
from abc import ABC, abstractmethod
from jivo_bot.repository import AbstractRepository
from jivo_bot.schemas import JivoRequest, ChatMessageSchema
from config import JIVO_KEY, JIVO_URL, MODEL_COMPLETION_URL, MODEL_COMPLETION_API_KEY
from loggers import logger


class ResponseStrategy(ABC):
    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    @abstractmethod
    async def generate_response(self, request: JivoRequest, history: List[ChatMessageSchema]):
        pass

    @abstractmethod
    async def get_dummy_answer(self):
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

    async def send_response(self, request: JivoRequest):
        client_id = request.client_id
        chat_id = request.chat_id
        channel_id = request.channel.id
        received_text = request.message.text

        dummy_answer = await self.get_dummy_answer()
        if dummy_answer:
            await self.send(client_id=client_id, chat_id=chat_id, text=dummy_answer)

        await self.save_request(client_id, chat_id, channel_id, received_text)

        history = await self.get_history(client_id, chat_id, channel_id)

        response_text = await self.generate_response(request, history)

        if not response_text:
            response_text = "Ошибка генерации ответа, повторите попытку позднее."

        if await self.send(client_id=client_id, chat_id=chat_id, text=response_text):
            await self.save_response(client_id, chat_id, channel_id, response_text)

    @staticmethod
    async def send(client_id, chat_id, text) -> bool:
        try:
            data = {
                "id": str(uuid.uuid4()),
                "client_id": client_id,
                "chat_id": chat_id,
                "message": {
                    "type": "TEXT",
                    "text": text,
                },
                "event": "BOT_MESSAGE"
            }
            url = f"{JIVO_URL}/{JIVO_KEY}"
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(url, json=data, headers=headers)
                if response.status_code != 200:
                    logger.error(f"Request error: {response}; url: {url}; Data: {data}")
                    return False

            return True

        except httpx.RequestError as err:
            logger.error(f"Request error: {err}")
            return False


class EchoStrategy(ResponseStrategy):
    async def generate_response(self, request: JivoRequest, history: List[ChatMessageSchema]) -> str:
        return f"{request.message.text!r}\n Recorded messages - {len(history)}"

    async def get_dummy_answer(self):
        return False


class OpenAIStrategy(ResponseStrategy):
    async def generate_response(self, request: JivoRequest, history: List[ChatMessageSchema]) -> Union[str, bool]:
        history_list = [{'from_bot': item.from_bot, 'text': item.text} for item in history][::-1]
        data = {
            "history": history_list
        }

        url = MODEL_COMPLETION_URL

        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json", "api-key": MODEL_COMPLETION_API_KEY}
            response = await client.post(url, json=data, headers=headers)
            if response.status_code != 200:
                logger.error(f"Request error: {response}; url: {url}; Data: {data}")
                return False

        res = json.loads(response.text)
        return res['response']

    async def get_dummy_answer(self):
        return random.choice([
            "Генерирую ответ...",
            "Один момент...",
            "Думаю...",
            "Ищу ответ на ваш запрос...",
            "Пожалуйста, подождите...",
            "Секунду...",
            "Анализирую запрос..."
        ])
