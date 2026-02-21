from typing import Optional, Annotated
from pydantic_resolve import LoadBy
from src.services.story.schema import Story as BaseStory
from src.services.task.schema import Task as BaseTask
from src.services.user.schema import User as BaseUser
from pydantic_resolve import serialization

class Task0(BaseTask):
    user: Annotated[Optional[BaseUser], LoadBy('owner_id')] = None

@serialization
class Story0(BaseStory):
    tasks: Annotated[list[Task0], LoadBy('id')] = []
    assignee: Annotated[Optional[BaseUser], LoadBy('owner_id')] = None
