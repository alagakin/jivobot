from jivo_bot.schemas import JivoRequest
from jivo_bot.exceptions import UnsupportedMessageType, UnsupportedEvent
from jivo_bot.strategies import ResponseStrategy


class RequestHandler:
    def __init__(self, strategy: ResponseStrategy):
        self.__strategy = strategy

    async def handle(self, request: JivoRequest):
        if request.message.type != 'TEXT':
            raise UnsupportedMessageType(
                f"Request message type {request.message.type!r} is not supported. Request: {request}")
        if request.event != 'CLIENT_MESSAGE':
            raise UnsupportedEvent(f"Event {request.event!r} is not supported. Request: {request}")

        return await self.__strategy.send_response(request)
