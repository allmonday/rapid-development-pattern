from pydantic import BaseModel
from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService
import src.db as db

import src.services.story.query as sq

from .schema import Story0
from .schema1 import Story1
from .schema2 import Story2
from .schema3 import Story3


class Payload(BaseModel):
    message: str = '123'
    name: str


class DemoService(UseCaseService):
    """Demo: Different pydantic-resolve patterns."""

    @query
    async def get_stories(cls, payload: Payload) -> list[Story0]:
        """Stories with basic AutoLoad pattern."""
        async with db.async_session() as session:
            stories = await sq.get_stories(session)
        stories = [Story0.model_validate(t) for t in stories]
        return await Resolver().resolve(stories)

    @query
    async def get_stories_1(cls) -> list[Story1]:
        """Stories with SendTo and Collector pattern."""
        async with db.async_session() as session:
            stories = await sq.get_stories(session)
        stories = [Story1.model_validate(t) for t in stories]
        return await Resolver().resolve(stories)

    @query
    async def get_stories_2(cls) -> list[Story2]:
        """Stories with post-processing for estimates."""
        async with db.async_session() as session:
            stories = await sq.get_stories(session)
        stories = [Story2.model_validate(t) for t in stories]
        return await Resolver().resolve(stories)

    @query
    async def get_stories_3(cls) -> list[Story3]:
        """Stories with ancestor context for full names."""
        async with db.async_session() as session:
            stories = await sq.get_stories(session)
        stories = [Story3.model_validate(t) for t in stories]
        return await Resolver().resolve(stories)
