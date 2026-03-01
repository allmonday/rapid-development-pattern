from pydantic import BaseModel, ConfigDict
from pydantic_resolve import Relationship, query, mutation
from typing import Optional
import src.services.story.schema as story_schema
import src.services.story.loader as story_loader
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_sprints as get_sprints_query
from . import mutation as sprint_mutation

class Sprint(BaseModel, BaseEntity):
    __pydantic_resolve_relationships__ = [
        Relationship( field='id', target_kls=list[story_schema.Story], loader=story_loader.sprint_to_story_loader, default_field_name='stories'),
    ]

    id: int
    name: str
    status: str
    team_id: int

    @query(name='get_sprints')
    async def get_sprints(cls) -> list['Sprint']:
        async with async_session() as session:
            sprints = await get_sprints_query(session)
            return [Sprint.model_validate(sprint) for sprint in sprints]

    # Mutation methods - Sprint 自身负责更新
    @mutation(name='updateSprint')
    async def update_sprint(cls, id: int, name: Optional[str] = None, status: Optional[str] = None) -> Optional['Sprint']:
        async with async_session() as session:
            sprint = await sprint_mutation.update_sprint(session, id, name, status)
            return Sprint.model_validate(sprint) if sprint else None

    # Mutation methods - 管理 Story 子实体
    @mutation(name='createStory')
    async def create_story(cls, sprint_id: int, name: str, owner_id: int) -> story_schema.Story:
        async with async_session() as session:
            story = await sprint_mutation.create_story(session, sprint_id, name, owner_id)
            return story_schema.Story.model_validate(story)

    @mutation(name='deleteStory')
    async def delete_story(cls, id: int) -> bool:
        async with async_session() as session:
            return await sprint_mutation.delete_story(session, id)

    model_config = ConfigDict(from_attributes=True)
