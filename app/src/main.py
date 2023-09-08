from fastapi import FastAPI
from jivo_bot.repository import ChatMessageRepository
from jivo_bot.schemas import JivoRequest
from jivo_bot.handler import RequestHandler
from jivo_bot.exceptions import UnsupportedMessageType, UnsupportedEvent
from jivo_bot.strategies import EchoStrategy
from loggers import logger
from config import JIVO_KEY

app = FastAPI()


@app.post(f"/{JIVO_KEY}")
async def root(request: JivoRequest):
    try:
        repository = ChatMessageRepository()
        strategy = EchoStrategy(repository)
        handler = RequestHandler(request, strategy)
        await handler.handle()
    except (UnsupportedMessageType, UnsupportedEvent) as e:
        logger.error(e)
