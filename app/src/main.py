import asyncio
from fastapi import FastAPI, Depends
from jivo_bot.repository import ChatMessageSQLRepository
from jivo_bot.schemas import JivoRequest
from jivo_bot.handler import RequestHandler
from jivo_bot.exceptions import UnsupportedMessageType, UnsupportedEvent
from jivo_bot.strategies import EchoStrategy
from loggers import logger
from config import JIVO_KEY

app = FastAPI()

user_locks = {}


@app.post(f"/{JIVO_KEY}")
async def root(request: JivoRequest, repository=Depends(ChatMessageSQLRepository)):
    try:
        key = (request.chat_id, request.client_id, request.channel.id)
        if key not in user_locks:
            user_locks[key] = asyncio.Lock()
        async with user_locks[key]:
            strategy = EchoStrategy(repository)
            handler = RequestHandler(request, strategy)
            await handler.handle()
    except (UnsupportedMessageType, UnsupportedEvent) as e:
        logger.error(e)
