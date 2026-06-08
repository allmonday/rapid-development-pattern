from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .model import Base

# Import all ORM models before mocks to ensure SQLAlchemy can resolve
# forward references in relationship() declarations
import src.services.user.model   # noqa: F401
import src.services.team.model   # noqa: F401
import src.services.sprint.model # noqa: F401
import src.services.story.model  # noqa: F401
import src.services.task.model   # noqa: F401

import src.services.sprint.mock as sm
import src.services.story.mock as stm
import src.services.task.mock as tm
import src.services.team.mock as tem
import src.services.team.model as team_model
import src.services.user.mock as um
import src.services.user.model as user_model
import src.services.sprint.model as sprint_model
import src.services.story.model as story_model
import src.services.task.model as task_model

engine = create_async_engine(
    "sqlite+aiosqlite://",
    echo=False,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def prepare():
    async with async_session() as session:
        async with session.begin():
            records = sm.sprints + stm.stories + tm.tasks + tem.team_users + tem.teams + um.users
            session.add_all(records)


async def prepare_large():
    """Seed a large dataset: 50 teams, 200 users, 150 sprints, 450 stories, 1350 tasks."""
    from sqlalchemy import select

    async with async_session() as session:
        async with session.begin():
            records = sm.sprints + stm.stories + tm.tasks + tem.team_users + tem.teams + um.users
            session.add_all(records)

    # Add large dataset on top
    n_teams = 50
    n_users = 200
    n_sprints_per_team = 3
    n_stories_per_sprint = 3
    n_tasks_per_story = 3

    async with async_session() as session:
        async with session.begin():
            # Users (id starts at 100)
            users = []
            for i in range(n_users):
                users.append(user_model.User(
                    id=100 + i,
                    name=f"User-{i}",
                    level="senior" if i % 3 == 0 else "junior",
                ))
            session.add_all(users)
        await session.commit()

    async with async_session() as session:
        async with session.begin():
            # Teams (id starts at 100)
            teams = []
            for i in range(n_teams):
                teams.append(team_model.Team(
                    id=100 + i,
                    name=f"Team-{i}",
                ))
            session.add_all(teams)
        await session.commit()

    async with async_session() as session:
        async with session.begin():
            # Team-User junction (4 users per team)
            team_users = []
            uid = 0
            for t in range(n_teams):
                for j in range(4):
                    team_users.append(team_model.TeamUser(
                        id=100 + t * 4 + j,
                        user_id=100 + (uid % n_users),
                        team_id=100 + t,
                    ))
                    uid += 1
            session.add_all(team_users)
        await session.commit()

    async with async_session() as session:
        async with session.begin():
            # Sprints (id starts at 100)
            sprints = []
            for t in range(n_teams):
                for s in range(n_sprints_per_team):
                    sprints.append(sprint_model.Sprint(
                        id=100 + t * n_sprints_per_team + s,
                        name=f"Sprint T{t}-W{s*2}",
                        status=["close", "active", "plan"][s % 3],
                        team_id=100 + t,
                    ))
            session.add_all(sprints)
        await session.commit()

    async with async_session() as session:
        async with session.begin():
            # Stories (id starts at 100)
            stories = []
            for sp in sprints:
                for st in range(n_stories_per_sprint):
                    stories.append(story_model.Story(
                        id=100 + (sp.id - 100) * n_stories_per_sprint + st,
                        name=f"Story-{sp.id}-{st}",
                        owner_id=100 + ((sp.id - 100) * n_stories_per_sprint + st) % n_users,
                        sprint_id=sp.id,
                    ))
            session.add_all(stories)
        await session.commit()

    async with async_session() as session:
        async with session.begin():
            # Tasks (id starts at 100)
            tasks = []
            for story in stories:
                for tk in range(n_tasks_per_story):
                    tasks.append(task_model.Task(
                        id=100 + (story.id - 100) * n_tasks_per_story + tk,
                        name=f"Task-{story.id}-{tk}",
                        owner_id=100 + ((story.id - 100) * n_tasks_per_story + tk) % n_users,
                        story_id=story.id,
                        estimate=2 + (tk * 3) % 8,
                    ))
            session.add_all(tasks)
        await session.commit()
