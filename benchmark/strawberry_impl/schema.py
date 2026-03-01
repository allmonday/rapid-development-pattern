"""Strawberry GraphQL schema definitions."""

import strawberry
from strawberry.types.info import Info
from typing import List, Optional


@strawberry.type
class UserType:
    """User type."""
    id: int
    name: str
    level: str


@strawberry.type
class TaskType:
    """Task type with lazy-loaded owner."""
    id: int
    name: str
    owner_id: int
    story_id: int
    estimate: int

    @strawberry.field
    async def owner(self, info: Info) -> Optional[UserType]:
        loader = info.context["loaders"].user_loader
        result = await loader.load(self.owner_id)
        if result:
            return UserType(id=result.id, name=result.name, level=result.level)
        return None


@strawberry.type
class StoryType:
    """Story type with lazy-loaded owner and tasks."""
    id: int
    name: str
    owner_id: int
    sprint_id: int

    @strawberry.field
    async def owner(self, info: Info) -> Optional[UserType]:
        loader = info.context["loaders"].user_loader
        result = await loader.load(self.owner_id)
        if result:
            return UserType(id=result.id, name=result.name, level=result.level)
        return None

    @strawberry.field
    async def tasks(self, info: Info) -> List[TaskType]:
        loader = info.context["loaders"].story_to_task_loader
        results = await loader.load(self.id)
        return [
            TaskType(
                id=r.id,
                name=r.name,
                owner_id=r.owner_id,
                story_id=r.story_id,
                estimate=r.estimate,
            )
            for r in results
        ]


@strawberry.type
class SprintType:
    """Sprint type with lazy-loaded stories."""
    id: int
    name: str
    status: str
    team_id: int

    @strawberry.field
    async def stories(self, info: Info) -> List[StoryType]:
        loader = info.context["loaders"].sprint_to_story_loader
        results = await loader.load(self.id)
        return [
            StoryType(
                id=r.id,
                name=r.name,
                owner_id=r.owner_id,
                sprint_id=r.sprint_id,
            )
            for r in results
        ]


@strawberry.type
class TeamType:
    """Team type with lazy-loaded sprints and users."""
    id: int
    name: str

    @strawberry.field
    async def sprints(self, info: Info) -> List[SprintType]:
        loader = info.context["loaders"].team_to_sprint_loader
        results = await loader.load(self.id)
        return [
            SprintType(
                id=r.id,
                name=r.name,
                status=r.status,
                team_id=r.team_id,
            )
            for r in results
        ]

    @strawberry.field
    async def users(self, info: Info) -> List[UserType]:
        loader = info.context["loaders"].team_to_user_loader
        results = await loader.load(self.id)
        return [
            UserType(id=r.id, name=r.name, level=r.level)
            for r in results
        ]
