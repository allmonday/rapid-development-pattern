from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService
import src.db as db

from .schema import Sample4TeamDetail
import src.services.team.query as tmq


class Sample4Service(UseCaseService):
    """Sample 4: Post-processing and data collection with Collector."""

    @query
    async def get_teams_with_detail(cls) -> list[Sample4TeamDetail]:
        """Teams with task counting and aggregation."""
        async with db.async_session() as session:
            teams = await tmq.get_teams(session)
        teams = [Sample4TeamDetail.model_validate(t) for t in teams]
        return await Resolver().resolve(teams)
