from pydantic import BaseModel, ConfigDict
from pydantic_resolve import Relationship, query
import src.services.sprint.schema as sprint_schema
import src.services.sprint.loader as sprint_loader
import src.services.user.schema as user_schema
import src.services.user.loader as user_loader
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_teams as get_teams_query

class Team(BaseModel, BaseEntity):
    __pydantic_resolve_relationships__ = [
        Relationship( field='id', target_kls=list[sprint_schema.Sprint], loader=sprint_loader.team_to_sprint_loader, default_field_name='sprints'),
        Relationship( field='id', target_kls=list[user_schema.User], loader=user_loader.team_to_user_loader, default_field_name='users'),
    ]

    id: int
    name: str

    @query(name='get_teams')
    async def get_teams(cls) -> list['Team']:
        async with async_session() as session:
            teams = await get_teams_query(session)
            return [Team.model_validate(team) for team in teams]


    model_config = ConfigDict(from_attributes=True)
