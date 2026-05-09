from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService

from .schema import Sample5Root


class Sample5Service(UseCaseService):
    """Sample 5: Database query within resolve method using context."""

    @query
    async def get_page_info(cls, team_id: int) -> Sample5Root:
        """Page info with team details resolved by context."""
        page = Sample5Root(summary="hello world")
        return await Resolver(context={'team_id': team_id}).resolve(page)
