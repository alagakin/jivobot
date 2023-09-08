from jivo_bot.schemas import JivoRequest
from jivo_bot.exceptions import UnsupportedMessageType, UnsupportedEvent
from jivo_bot.strategies import ResponseStrategy


class RequestHandler:
    def __init__(self, request: JivoRequest, strategy: ResponseStrategy):
        self.__request = request
        self.__strategy = strategy

    async def handle(self):
        if self.__request.message.type != 'TEXT':
            raise UnsupportedMessageType(
                f"Request message type {self.__request.message.type!r} is not supported. Request: {self.__request}")
        if self.__request.event != 'CLIENT_MESSAGE':
            raise UnsupportedEvent(f"Event {self.__request.event!r} is not supported. Request: {self.__request}")

        return await self.__strategy.send_response(self.__request)
