from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService
import src.db as db

import src.services.user.schema as us
import src.services.task.schema as ts

import src.services.user.query as uq
import src.services.task.query as tq
import src.services.story.query as sq
import src.services.sprint.query as spq
import src.services.team.query as tmq

from .schema import (
    Sample1TaskDetail,
    Sample1StoryDetail,
    Sample1SprintDetail,
    Sample1TeamDetail,
    Sample1TeamDetail2)


class Sample1Service(UseCaseService):
    """Sample 1: Basic nested data loading with AutoLoad."""

    @query
    async def get_users(cls) -> list[us.User]:
        """Return list of users."""
        async with db.async_session() as session:
            return await uq.get_users(session)

    @query
    async def get_tasks(cls) -> list[ts.Task]:
        """Return list of tasks."""
        async with db.async_session() as session:
            return await tq.get_tasks(session)

    @query
    async def get_tasks_with_detail(cls) -> list[Sample1TaskDetail]:
        """Return list of tasks with user details."""
        async with db.async_session() as session:
            tasks = await tq.get_tasks(session)
        tasks = [Sample1TaskDetail.model_validate(t) for t in tasks]
        return await Resolver().resolve(tasks)

    @query
    async def get_stories_with_detail(cls) -> list[Sample1StoryDetail]:
        """Return list of stories with tasks and users."""
        async with db.async_session() as session:
            stories = await sq.get_stories(session)
        stories = [Sample1StoryDetail.model_validate(t) for t in stories]
        return await Resolver().resolve(stories)

    @query
    async def get_sprints_with_detail(cls) -> list[Sample1SprintDetail]:
        """Return list of sprints with stories, tasks and users."""
        async with db.async_session() as session:
            sprints = await spq.get_sprints(session)
        sprints = [Sample1SprintDetail.model_validate(t) for t in sprints]
        return await Resolver().resolve(sprints)

    @query
    async def get_teams_with_detail(cls) -> list[Sample1TeamDetail]:
        """Return list of teams with sprints, stories, tasks and users."""
        async with db.async_session() as session:
            teams = await tmq.get_teams(session)
        teams = [Sample1TeamDetail.model_validate(t) for t in teams]
        return await Resolver().resolve(teams)

    @query
    async def get_teams_with_detail_2(cls) -> list[Sample1TeamDetail2]:
        """Return list of teams with hardcoded sprint data."""
        teams = [{
            "id": 1,
            "name": "team-A",
            "sprints": [
                {"id": 1, "name": "Sprint A W1", "status": "close", "team_id": 1},
                {"id": 2, "name": "Sprint A W3", "status": "active", "team_id": 1},
                {"id": 3, "name": "Sprint A W5", "status": "plan", "team_id": 1},
            ]
        }]
        teams = [Sample1TeamDetail2.model_validate(t) for t in teams]
        return await Resolver().resolve(teams)
