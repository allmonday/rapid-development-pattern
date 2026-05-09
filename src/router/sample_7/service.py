from collections import defaultdict

from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService
import src.db as db

import src.services.user.query as uq
import src.services.story.query as sq
import src.services.sprint.query as spq
import src.services.team.query as tq
import src.services.task.query as tskq

from .schema import (
    SprintToStoryLoader,
    TeamToSprintLoader,
    UserLoader,
    Sample7TeamDetail,
    Sample7TaskDetail)


def _add_to_loader(loader, items, get_key):
    _map = defaultdict(list)
    for item in items:
        _map[get_key(item)].append(item)
    for k, v in _map.items():
        loader.prime(k, v)

def _add_single_to_loader(loader, items, get_key):
    _map = {}
    for item in items:
        _map[get_key(item)] = item
    for k, v in _map.items():
        loader.prime(k, v)


class Sample7Service(UseCaseService):
    """Sample 7: Manual loader instance management."""

    @query
    async def get_tasks(cls) -> list[Sample7TaskDetail]:
        """Tasks with pre-loaded user data."""
        async with db.async_session() as session:
            users = await uq.get_users(session)
            user_loader = UserLoader()
            _add_single_to_loader(user_loader, users, lambda u: u.id)

            tasks = await tskq.get_tasks(session)
        tasks = [Sample7TaskDetail.model_validate(t) for t in tasks]
        return await Resolver(loader_instances={UserLoader: user_loader}).resolve(tasks)

    @query
    async def get_user_stat(cls, id: int) -> list[Sample7TeamDetail]:
        """User statistics with full hierarchy via manual loaders."""
        async with db.async_session() as session:
            sprint_to_story_loader = SprintToStoryLoader()
            team_to_sprint_loader = TeamToSprintLoader()

            users = await uq.get_user_by_ids([id], session)
            stories = await sq.get_stories_by_owner_ids([u.id for u in users], session)
            _add_to_loader(sprint_to_story_loader, stories, lambda s: s.sprint_id)

            sprint_ids = list({s.sprint_id for s in stories})
            sprints = await spq.get_sprints_by_ids(sprint_ids, session)
            _add_to_loader(team_to_sprint_loader, sprints, lambda s: s.team_id)

            team_ids = list({s.team_id for s in sprints})
            teams = await tq.get_team_by_ids(team_ids, session)
        teams = [Sample7TeamDetail.model_validate(t) for t in teams]
        return await Resolver(loader_instances={
            SprintToStoryLoader: sprint_to_story_loader,
            TeamToSprintLoader: team_to_sprint_loader,
        }).resolve(teams)
