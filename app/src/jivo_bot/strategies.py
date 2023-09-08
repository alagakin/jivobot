import json
import requests
from abc import ABC, abstractmethod
from jivo_bot.schemas import JivoRequest
from config import JIVO_KEY, JIVO_URL


class ResponseStrategy(ABC):
    @abstractmethod
    async def send_response(self, request: JivoRequest):
        pass


class EchoStrategy(ResponseStrategy):
    async def send_response(self, request: JivoRequest):
        data = {
            "id": request.id,
            "client_id": request.client_id,
            "chat_id": request.chat_id,
            "message": {
                "type": "TEXT",
                "text": request.message.text,
            },
            "event": "BOT_MESSAGE"
        }
        url = f"{JIVO_URL}/{JIVO_KEY}"
        json_data = json.dumps(data)
        requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})


class OpenAIStrategy(ResponseStrategy, ABC):
    pass
