from sqlalchemy import Column, Integer, String, Boolean

from jivo_bot.schemas import ChatMessageSchema


from database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    client_id = Column(String)
    chat_id = Column(String)
    channel_id = Column(String)
    from_bot = Column(Boolean)
    text = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_read_model(self) -> ChatMessageSchema:
        return ChatMessageSchema(
            id=self.id,
            client_id=self.client_id,
            chat_id=self.chat_id,
            channel_id=self.chat_id,
            from_bot=self.from_bot,
            text=self.text
        )
