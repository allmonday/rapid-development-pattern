from typing import Optional, Annotated
from pydantic_resolve import DefineSubset, SubsetConfig, serialization
from src.services.er_diagram import AutoLoad
from src.services.story.schema import Story as BaseStory

from src.services.task.schema import Task as BaseTask
from src.services.user.schema import User as BaseUser


# post case 1
class Task3(BaseTask):
    user: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None

    fullname: str = ''
    def post_fullname(self, ancestor_context):  # Access story.name from parent context
        return f'{ancestor_context["story_name"]} - {self.name}'

@serialization
class Story3(DefineSubset):
    __subset__ = SubsetConfig(
        kls=BaseStory,
        fields=['id', 'name', 'owner_id'],
        expose_as=[('name', 'story_name')]
    )

    tasks: Annotated[list[Task3], AutoLoad()] = []
    assignee: Annotated[Optional[BaseUser], AutoLoad(origin='owner')] = None
