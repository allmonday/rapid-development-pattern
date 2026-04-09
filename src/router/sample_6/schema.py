from typing import Optional, Annotated
from pydantic_resolve import DefineSubset, SubsetConfig, serialization
from pydantic import BaseModel, Field
import src.db as db

import src.services.story.schema as ss
import src.services.task.schema as ts
import src.services.user.schema as us
import src.services.sprint.schema as sps
import src.services.team.schema as tms
from src.services.er_diagram import AutoLoad

import src.services.team.query as tmq

class Sample6TaskDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=ts.Task,
        fields=['name', 'owner_id'],
        excluded_fields=['owner_id'])

    def post_name(self):
        return 'task name: ' + self.name

    user: Annotated[Optional[us.User], AutoLoad(origin='owner')] = None


class Sample6StoryDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=ss.Story,
        fields=['name', 'id'],
        excluded_fields=['id']
    )

    def post_name(self):
        return 'story name: ' + self.name

    tasks: Annotated[list[Sample6TaskDetail], AutoLoad()] = []

class Sample6SprintDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=sps.Sprint,
        fields=('name', 'id'),
        excluded_fields=['id'])

    def post_name(self):
        return 'sprint name: ' + self.name

    stories: Annotated[list[Sample6StoryDetail], AutoLoad()] = []

class Sample6TeamDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=tms.Team,
        fields=['id', 'name'],
        excluded_fields=['id'])

    def post_name(self):
        return 'team name: ' + self.name

    sprints: Annotated[list[Sample6SprintDetail], AutoLoad()] = []

@serialization
class Sample6Root(BaseModel):
    summary: str
    teams: list[Sample6TeamDetail] = []
    async def resolve_teams(self):
        async with db.async_session() as session:
            teams = await tmq.get_teams(session)
            return teams
