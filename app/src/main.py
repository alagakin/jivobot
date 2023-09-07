from fastapi import FastAPI
from schemas import JivoRequest
from handler import RequestHandler
from exceptions import UnsupportedMessageType, UnsupportedEvent
from strategies import EchoStrategy
from loggers import logger
from config import JIVO_KEY
app = FastAPI()


@app.post(f"/{JIVO_KEY}")
async def root(request: JivoRequest):
    try:
        strategy = EchoStrategy()
        handler = RequestHandler(request, strategy)
        await handler.handle()
    except (UnsupportedMessageType, UnsupportedEvent) as e:
        logger.error(e)
