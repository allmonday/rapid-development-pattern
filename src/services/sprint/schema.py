from pydantic import BaseModel, ConfigDict
from pydantic_resolve import Relationship, query
import src.services.story.schema as story_schema
import src.services.story.loader as story_loader
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_sprints as get_sprints_query

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

    model_config = ConfigDict(from_attributes=True)
