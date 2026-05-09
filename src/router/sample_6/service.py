from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService

from .schema import Sample6Root


class Sample6Service(UseCaseService):
    """Sample 6: Dynamic data loading from resolve methods."""

    @query
    async def get_page_info(cls) -> Sample6Root:
        """Page info with all teams resolved dynamically."""
        page = Sample6Root(summary="hello world")
        return await Resolver().resolve(page)
