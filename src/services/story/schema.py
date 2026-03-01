from pydantic import BaseModel, ConfigDict
from pydantic_resolve import Relationship, query, mutation
from typing import Optional
import src.services.task.loader as task_loader
import src.services.user.loader as user_loader
import src.services.user.schema as user_schema
import src.services.task.schema as task_schema
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_stories as get_stories_query
from . import mutation as story_mutation

class Story(BaseModel, BaseEntity):
    __pydantic_resolve_relationships__ = [
        Relationship( field='id', target_kls=list[task_schema.Task], loader=task_loader.story_to_task_loader, default_field_name='tasks'),
        Relationship( field='owner_id', target_kls=user_schema.User, loader=user_loader.user_batch_loader, default_field_name='owner'),
    ]

    id: int
    name: str
    owner_id: int
    sprint_id: int

    @query(name='get_stories')
    async def get_stories(cls) -> list['Story']:
        async with async_session() as session:
            stories = await get_stories_query(session)
            return [Story.model_validate(story) for story in stories]

    # Mutation methods - Story 自身负责更新
    @mutation(name='updateStory')
    async def update_story(cls, id: int, name: Optional[str] = None, owner_id: Optional[int] = None) -> Optional['Story']:
        async with async_session() as session:
            story = await story_mutation.update_story(session, id, name, owner_id)
            return Story.model_validate(story) if story else None

    # Mutation methods - 管理 Task 子实体
    @mutation(name='createTask')
    async def create_task(cls, story_id: int, name: str, owner_id: int, estimate: int = 0) -> task_schema.Task:
        async with async_session() as session:
            task = await story_mutation.create_task(session, story_id, name, owner_id, estimate)
            return task_schema.Task.model_validate(task)

    @mutation(name='deleteTask')
    async def delete_task(cls, id: int) -> bool:
        async with async_session() as session:
            return await story_mutation.delete_task(session, id)

    model_config = ConfigDict(from_attributes=True)

