from pydantic import BaseModel, ConfigDict
from src.services.er_diagram import BaseEntity
from pydantic_resolve import query
from src.db import async_session
from .query import get_users as get_users_query

class User(BaseModel, BaseEntity):
    __relationships__ = []
    id: int
    name: str
    level: str

    @query(name='get_users')
    async def get_users(cls) -> list['User']:
        async with async_session() as session:
            users = await get_users_query(session)
            return [User.model_validate(user) for user in users]

    model_config = ConfigDict(from_attributes=True)