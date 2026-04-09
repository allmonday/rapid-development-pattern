from typing import Optional, Annotated
from pydantic_resolve import SubsetConfig, DefineSubset, serialization
from typing import Dict

import src.services.story.schema as ss
import src.services.task.schema as ts
import src.services.user.schema as us
import src.services.sprint.schema as sps
import src.services.team.schema as tms
from src.services.er_diagram import AutoLoad

class Sample3TaskDetail(ts.Task):
    user: Annotated[Optional[us.User], AutoLoad(origin='owner')] = None

    full_name: str = ''
    def resolve_full_name(self, ancestor_context: Dict):
        team = ancestor_context['team_name']
        sprint = ancestor_context['sprint_name']
        story = ancestor_context['story_name']
        return f"{team}/{sprint}/{story}/{self.name}"

class Sample3StoryDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=ss.Story,
        fields="all",
        expose_as=[('name', 'story_name')]
    )
    tasks: Annotated[list[Sample3TaskDetail], AutoLoad()] = []

class Sample3SprintDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=sps.Sprint,
        fields="all",
        expose_as=[('name', 'sprint_name')]
    )

    stories: Annotated[list[Sample3StoryDetail], AutoLoad()] = []

@serialization
class Sample3TeamDetail(DefineSubset):
    __subset__ = SubsetConfig(
        kls=tms.Team,
        fields="all",
        expose_as=[('name', 'team_name')]
    )

    sprints: Annotated[list[Sample3SprintDetail], AutoLoad()] = []
