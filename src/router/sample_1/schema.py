from __future__ import annotations

from typing import Optional, Annotated
from pydantic_resolve import serialization
from src.services.er_diagram import AutoLoad

import src.services.story.schema as ss
import src.services.task.schema as ts
import src.services.user.schema as us
import src.services.sprint.schema as sps
import src.services.team.schema as tms


@serialization
class Sample1TeamDetail(tms.Team):
    sprints: Annotated[list[Sample1SprintDetail], AutoLoad()] = []
    members: Annotated[list[us.User], AutoLoad(origin='users')] = []

@serialization
class Sample1TeamDetail2(tms.Team):
    sprints: list[Sample1SprintDetail] = []
    members: Annotated[list[us.User], AutoLoad(origin='users')] = []

@serialization
class Sample1TaskDetail(ts.Task):
    user: Annotated[Optional[us.User], AutoLoad(origin='owner')] = None

@serialization
class Sample1SprintDetail(sps.Sprint):
    stories: Annotated[list[Sample1StoryDetail], AutoLoad()]  = []

@serialization
class Sample1StoryDetail(ss.Story):
    tasks: Annotated[list[Sample1TaskDetail], AutoLoad()] = []
    owner: Annotated[Optional[us.User], AutoLoad()] = None
