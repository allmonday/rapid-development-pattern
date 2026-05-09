from typing import Optional, Annotated
from pydantic_resolve import DefineSubset, serialization
from pydantic_resolve import AutoLoad
from src.services.story.schema import Story as BaseStory
from src.services.task.schema import Task as BaseTask
from src.services.user.schema import User as BaseUser


# post case 1
class Task2(BaseTask):
    user: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None

@serialization
class Story2(DefineSubset):
    __subset__ = (BaseStory, ('id', 'name', 'owner_id'))

    tasks: list[Task2] = []
    assignee: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None

    total_estimate: int = 0
    def post_total_estimate(self):
        return sum(task.estimate for task in self.tasks)
