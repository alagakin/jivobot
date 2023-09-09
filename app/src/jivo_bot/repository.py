from abc import abstractmethod, ABC
from sqlalchemy import insert, select

from database import async_session_maker
from jivo_bot.models import ChatMessage


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        pass

    @abstractmethod
    async def find_all(self):
        pass

    @abstractmethod
    async def query(self, filters: dict = None):
        pass


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_all(self):
        async with async_session_maker() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            res = [row[0].to_read_model() for row in res.all()]
            return res

    async def query(self, filters: dict = None):
        async with async_session_maker() as session:
            stmt = select(self.model)

            if filters:
                for key, value in filters.items():
                    stmt = stmt.filter(getattr(self.model, key) == value)

            result = await session.execute(stmt)
            rows = result.scalars().all()

            results = [row.to_read_model() for row in rows]
            return results


class ChatMessageSQLRepository(SQLAlchemyRepository):
    model = ChatMessage
