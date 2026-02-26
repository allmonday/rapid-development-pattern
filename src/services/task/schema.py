from pydantic import BaseModel, ConfigDict
from src.services.er_diagram import BaseEntity
from pydantic_resolve import Relationship, query
import src.services.user.loader as user_loader
import src.services.user.schema as user_schema
from src.db import async_session
from .query import get_tasks as get_tasks_query

class Task(BaseModel, BaseEntity):
    __pydantic_resolve_relationships__ = [
        Relationship( field='owner_id', target_kls=user_schema.User, loader=user_loader.user_batch_loader, default_field_name='owner'),
    ]

    id: int
    name: str
    owner_id: int
    story_id: int
    estimate: int

    @query(name='get_tasks')
    async def get_tasks(cls) -> list['Task']:
        async with async_session() as session:
            tasks = await get_tasks_query(session)
            return [Task.model_validate(task) for task in tasks]

    model_config = ConfigDict(from_attributes=True)