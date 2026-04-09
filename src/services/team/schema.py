from pydantic import BaseModel, ConfigDict
from pydantic_resolve import query, mutation
from typing import Optional
import src.services.sprint.schema as sprint_schema
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_teams as get_teams_query
from . import mutation as team_mutation

class Team(BaseModel, BaseEntity):
    __relationships__ = []

    id: int
    name: str

    @query
    async def get_teams(cls) -> list['Team']:
        async with async_session() as session:
            teams = await get_teams_query(session)
            return [Team.model_validate(team) for team in teams]

    # Mutation methods - Team 自身的 CRUD
    @mutation
    async def create_team(cls, name: str) -> 'Team':
        async with async_session() as session:
            team = await team_mutation.create_team(session, name)
            return Team.model_validate(team)

    @mutation
    async def update_team(cls, id: int, name: Optional[str] = None) -> Optional['Team']:
        async with async_session() as session:
            team = await team_mutation.update_team(session, id, name)
            return Team.model_validate(team) if team else None

    @mutation
    async def delete_team(cls, id: int) -> bool:
        async with async_session() as session:
            return await team_mutation.delete_team(session, id)

    # Mutation methods - 管理 Sprint 子实体
    @mutation
    async def create_sprint(cls, team_id: int, name: str, status: str = 'planning') -> sprint_schema.Sprint:
        async with async_session() as session:
            sprint = await team_mutation.create_sprint(session, team_id, name, status)
            return sprint_schema.Sprint.model_validate(sprint)

    @mutation
    async def delete_sprint(cls, id: int) -> bool:
        async with async_session() as session:
            return await team_mutation.delete_sprint(session, id)

    # Mutation methods - 团队成员管理
    @mutation
    async def add_team_member(cls, team_id: int, user_id: int) -> bool:
        async with async_session() as session:
            return await team_mutation.add_team_member(session, team_id, user_id)

    @mutation
    async def remove_team_member(cls, team_id: int, user_id: int) -> bool:
        async with async_session() as session:
            return await team_mutation.remove_team_member(session, team_id, user_id)

    model_config = ConfigDict(from_attributes=True)
