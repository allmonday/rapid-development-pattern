from typing import Optional, Annotated
from pydantic_resolve import Loader, serialization
from src.services.er_diagram import AutoLoad
from pydantic import BaseModel
import src.db as db

import src.services.story.schema as ss
import src.services.task.schema as ts
import src.services.user.schema as us
import src.services.sprint.schema as sps
import src.services.team.schema as tms

import src.services.team.query as tmq

class Sample5TaskDetail(ts.Task):
    user: Annotated[Optional[us.User], AutoLoad(origin='owner')] = None

class Sample5StoryDetail(ss.Story):
    tasks: Annotated[list[Sample5TaskDetail], AutoLoad()] = []

    task_count: int = 0
    def post_task_count(self):
        return len(self.tasks)

class Sample5SprintDetail(sps.Sprint):
    stories: Annotated[list[Sample5StoryDetail], AutoLoad()] = []

    task_count: int = 0
    def post_task_count(self):
        return sum([s.task_count for s in self.stories])

class Sample5TeamDetail(tms.Team):
    sprints: Annotated[list[Sample5SprintDetail], AutoLoad()] = []

    task_count: int = 0
    def post_task_count(self):
        return sum([s.task_count for s in self.sprints])

    description: str = ''
    def post_default_handler(self):
        self.description = f'team: "{self.name}" has {self.task_count} tasks in total.'


@serialization
class Sample5Root(BaseModel):
    summary: str
    team: Optional[Sample5TeamDetail] = None
    async def resolve_team(self, context):
        async with db.async_session() as session:
            team_id = context['team_id']
            team = await tmq.get_team_by_id(session, team_id)
            return team
