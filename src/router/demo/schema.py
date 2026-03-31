from typing import Optional, Annotated
from src.services.er_diagram import AutoLoad
from src.services.story.schema import Story as BaseStory
from src.services.task.schema import Task as BaseTask
from src.services.user.schema import User as BaseUser
from pydantic_resolve import serialization

class Task0(BaseTask):
    user: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None

@serialization
class Story0(BaseStory):
    tasks: Annotated[list[Task0], AutoLoad()] = []
    assignee: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None
