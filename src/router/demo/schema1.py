from typing import Optional, Annotated
from pydantic_resolve import Collector, DefineSubset, SendTo, serialization
from src.services.er_diagram import AutoLoad
from src.services.story.schema import Story as BaseStory
from src.services.task.schema import Task as BaseTask
from src.services.user.schema import User as BaseUser


# post case 1
class Task1(BaseTask):
    user: Annotated[
        Optional[BaseUser],
        AutoLoad(origin='owner'),
        SendTo('related_users')] = None

@serialization
class Story1(DefineSubset):
    __subset__ = (BaseStory, ('id', 'name', 'owner_id'))

    tasks: Annotated[list[Task1], AutoLoad()] = []
    assignee: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None

    related_users: list[BaseUser] = []
    def post_related_users(self, collector=Collector(alias='related_users')):
        return collector.values()
