from pydantic import BaseModel, ConfigDict
from pydantic_resolve import Relationship, query
import src.services.task.loader as task_loader
import src.services.user.loader as user_loader
import src.services.user.schema as user_schema
import src.services.task.schema as task_schema
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_stories as get_stories_query

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

    model_config = ConfigDict(from_attributes=True)

