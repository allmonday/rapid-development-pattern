from pydantic import BaseModel, ConfigDict
from src.services.er_diagram import BaseEntity
from pydantic_resolve import Relationship, query, mutation
from typing import Optional
import src.services.user.loader as user_loader
import src.services.user.schema as user_schema
from src.db import async_session
from .query import get_tasks as get_tasks_query
from . import mutation as task_mutation

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

    # Mutation methods - Task 自身负责更新
    @mutation(name='updateTask')
    async def update_task(cls, id: int, name: Optional[str] = None, owner_id: Optional[int] = None, estimate: Optional[int] = None) -> Optional['Task']:
        async with async_session() as session:
            task = await task_mutation.update_task(session, id, name, owner_id, estimate)
            return Task.model_validate(task) if task else None

    model_config = ConfigDict(from_attributes=True)