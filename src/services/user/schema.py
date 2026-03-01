from pydantic import BaseModel, ConfigDict
from src.services.er_diagram import BaseEntity
from pydantic_resolve import query, mutation
from typing import Optional
from src.db import async_session
from .query import get_users as get_users_query
from . import mutation as user_mutation

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

    @mutation(name='createUser')
    async def create_user(cls, name: str, level: str = 'user') -> 'User':
        async with async_session() as session:
            user = await user_mutation.create_user(session, name, level)
            return User.model_validate(user)

    @mutation(name='updateUser')
    async def update_user(cls, id: int, name: Optional[str] = None, level: Optional[str] = None) -> Optional['User']:
        async with async_session() as session:
            user = await user_mutation.update_user(session, id, name, level)
            return User.model_validate(user) if user else None

    @mutation(name='deleteUser')
    async def delete_user(cls, id: int) -> bool:
        async with async_session() as session:
            return await user_mutation.delete_user(session, id)

    model_config = ConfigDict(from_attributes=True)