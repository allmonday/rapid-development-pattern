"""Strawberry DataLoader implementations using strawberry.dataloader."""

from collections import defaultdict
from typing import List, Dict, Optional
from strawberry.dataloader import DataLoader
from sqlalchemy import select

import src.db as db


class Loaders:
    """Centralized DataLoader management for Strawberry."""

    def __init__(self):
        self._loaders: Dict[str, DataLoader] = {}

    def _get_or_create_loader(
        self,
        name: str,
        batch_load_fn
    ) -> DataLoader:
        """Get or create a DataLoader instance."""
        if name not in self._loaders:
            self._loaders[name] = DataLoader(batch_load_fn)
        return self._loaders[name]

    @property
    def user_loader(self) -> DataLoader:
        """Load users by ID."""
        async def batch_load(keys: List[int]) -> List[Optional[object]]:
            from src.services.user.model import User

            async with db.async_session() as session:
                result = await session.execute(
                    select(User).where(User.id.in_(keys))
                )
                users = result.scalars().all()
                user_map = {u.id: u for u in users}
                return [user_map.get(k) for k in keys]

        return self._get_or_create_loader("user", batch_load)

    @property
    def team_to_sprint_loader(self) -> DataLoader:
        """Load sprints by team ID."""
        async def batch_load(team_ids: List[int]) -> List[List[object]]:
            from src.services.sprint.model import Sprint

            async with db.async_session() as session:
                result = await session.execute(
                    select(Sprint).where(Sprint.team_id.in_(team_ids))
                )
                sprints = result.scalars().all()
                sprint_map = defaultdict(list)
                for s in sprints:
                    sprint_map[s.team_id].append(s)
                return [sprint_map.get(tid, []) for tid in team_ids]

        return self._get_or_create_loader("team_to_sprint", batch_load)

    @property
    def team_to_user_loader(self) -> DataLoader:
        """Load users by team ID via TeamUser junction table."""
        async def batch_load(team_ids: List[int]) -> List[List[object]]:
            from src.services.user.model import User
            from src.services.team.model import TeamUser

            async with db.async_session() as session:
                stmt = (
                    select(TeamUser.team_id, User)
                    .join(TeamUser, TeamUser.user_id == User.id)
                    .where(TeamUser.team_id.in_(team_ids))
                )
                rows = await session.execute(stmt)
                user_map = defaultdict(list)
                for row in rows:
                    user_map[row.team_id].append(row.User)
                return [user_map.get(tid, []) for tid in team_ids]

        return self._get_or_create_loader("team_to_user", batch_load)

    @property
    def sprint_to_story_loader(self) -> DataLoader:
        """Load stories by sprint ID."""
        async def batch_load(sprint_ids: List[int]) -> List[List[object]]:
            from src.services.story.model import Story

            async with db.async_session() as session:
                result = await session.execute(
                    select(Story).where(Story.sprint_id.in_(sprint_ids))
                )
                stories = result.scalars().all()
                story_map = defaultdict(list)
                for s in stories:
                    story_map[s.sprint_id].append(s)
                return [story_map.get(sid, []) for sid in sprint_ids]

        return self._get_or_create_loader("sprint_to_story", batch_load)

    @property
    def story_to_task_loader(self) -> DataLoader:
        """Load tasks by story ID."""
        async def batch_load(story_ids: List[int]) -> List[List[object]]:
            from src.services.task.model import Task

            async with db.async_session() as session:
                result = await session.execute(
                    select(Task).where(Task.story_id.in_(story_ids))
                )
                tasks = result.scalars().all()
                task_map = defaultdict(list)
                for t in tasks:
                    task_map[t.story_id].append(t)
                return [task_map.get(sid, []) for sid in story_ids]

        return self._get_or_create_loader("story_to_task", batch_load)
