import asyncio

from fastapi import FastAPI, Depends
from loggers import logger

from jivo_bot.repository import ChatMessageSQLRepository
from jivo_bot.schemas import JivoRequest
from jivo_bot.handler import RequestHandler
from jivo_bot.exceptions import UnsupportedMessageType, UnsupportedEvent
from jivo_bot.strategies import EchoStrategy, OpenAIStrategy
from config import JIVO_KEY

app = FastAPI()
user_locks = {}


async def get_open_ai_handler() -> RequestHandler:
    repository = ChatMessageSQLRepository()
    strategy = OpenAIStrategy(repository)
    return RequestHandler(strategy)


async def get_echo_handler() -> RequestHandler:
    repository = ChatMessageSQLRepository()
    strategy = EchoStrategy(repository)
    return RequestHandler(strategy)


@app.post(f"/{JIVO_KEY}")
async def root(request: JivoRequest, handler=Depends(get_open_ai_handler)):
    try:
        key = (request.chat_id, request.client_id, request.channel.id)
        if key not in user_locks:
            user_locks[key] = asyncio.Lock()
        async with user_locks[key]:
            await handler.handle(request)
    except (UnsupportedMessageType, UnsupportedEvent) as e:
        logger.error(e)
