"""Strawberry GraphQL resolvers."""

import strawberry
from strawberry.types.info import Info
from typing import List
from sqlalchemy import select
import src.db as db

from .schema import UserType, TeamType, SprintType, StoryType, TaskType


@strawberry.type
class Query:
    """Root query type."""

    @strawberry.field(name='get_users')
    async def get_users(self, info: Info) -> List[UserType]:
        """Get all users."""
        from src.services.user.model import User

        async with db.async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return [UserType(id=u.id, name=u.name, level=u.level) for u in users]

    @strawberry.field(name='get_teams')
    async def get_teams(self, info: Info) -> List[TeamType]:
        """Get all teams."""
        from src.services.team.model import Team

        async with db.async_session() as session:
            result = await session.execute(select(Team))
            teams = result.scalars().all()
            return [TeamType(id=t.id, name=t.name) for t in teams]

    @strawberry.field(name='get_sprints')
    async def get_sprints(self, info: Info) -> List[SprintType]:
        """Get all sprints."""
        from src.services.sprint.model import Sprint

        async with db.async_session() as session:
            result = await session.execute(select(Sprint))
            sprints = result.scalars().all()
            return [
                SprintType(id=s.id, name=s.name, status=s.status, team_id=s.team_id)
                for s in sprints
            ]

    @strawberry.field(name='get_stories')
    async def get_stories(self, info: Info) -> List[StoryType]:
        """Get all stories."""
        from src.services.story.model import Story

        async with db.async_session() as session:
            result = await session.execute(select(Story))
            stories = result.scalars().all()
            return [
                StoryType(id=s.id, name=s.name, owner_id=s.owner_id, sprint_id=s.sprint_id)
                for s in stories
            ]

    @strawberry.field(name='get_tasks')
    async def get_tasks(self, info: Info) -> List[TaskType]:
        """Get all tasks."""
        from src.services.task.model import Task

        async with db.async_session() as session:
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            return [
                TaskType(
                    id=t.id,
                    name=t.name,
                    owner_id=t.owner_id,
                    story_id=t.story_id,
                    estimate=t.estimate,
                )
                for t in tasks
            ]
