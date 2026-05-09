from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService
import src.db as db

from .schema import Sample3TeamDetail
import src.services.team.query as tmq


class Sample3Service(UseCaseService):
    """Sample 3: Expose ancestor data to descendant nodes."""

    @query
    async def get_teams_with_detail(cls) -> list[Sample3TeamDetail]:
        """Teams with ancestor context exposed to descendants."""
        async with db.async_session() as session:
            teams = await tmq.get_teams(session)
        teams = [Sample3TeamDetail.model_validate(t) for t in teams]
        return await Resolver().resolve(teams)
