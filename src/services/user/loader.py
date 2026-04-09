from collections import defaultdict
from .model import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import src.db as db
import src.services.team.model as tm
from aiodataloader import DataLoader

# user_id -> user
async def batch_get_users_by_ids(session: AsyncSession, user_ids: list[int]):
    users = (await session.execute(select(User).where(User.id.in_(user_ids)))).scalars().all()
    return users

# team -> user (level filter)
class UserByLevelLoader(DataLoader):
    level: str = ''

    async def batch_load_fn(self, team_ids: list[int]):
        async with db.async_session() as session:
            stmt = (select(tm.TeamUser.team_id, User)
                    .join(tm.TeamUser, tm.TeamUser.user_id == User.id)
                    .where(tm.TeamUser.team_id.in_(team_ids))
                    .where(User.level == self.level))
            pairs = (await session.execute(stmt))
            dct = defaultdict(list)
            for pair in pairs:
                dct[pair.team_id].append(pair.User)
            return [dct.get(team_id, []) for team_id in team_ids]
