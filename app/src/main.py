from fastapi import FastAPI, Depends
from jivo_bot.repository import ChatMessageSQLRepository
from jivo_bot.schemas import JivoRequest
from jivo_bot.handler import RequestHandler
from jivo_bot.exceptions import UnsupportedMessageType, UnsupportedEvent
from jivo_bot.strategies import EchoStrategy
from loggers import logger
from config import JIVO_KEY

app = FastAPI()


@app.post(f"/{JIVO_KEY}")
async def root(request: JivoRequest, repository=Depends(ChatMessageSQLRepository)):
    try:
        strategy = EchoStrategy(repository)
        handler = RequestHandler(request, strategy)
        await handler.handle()
    except (UnsupportedMessageType, UnsupportedEvent) as e:
        logger.error(e)
