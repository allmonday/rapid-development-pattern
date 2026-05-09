from pydantic_resolve import query, Resolver
from pydantic_resolve.use_case import UseCaseService
import src.db as db

from .schema import Sample2TeamDetail, Sample2TeamDetailMultipleLevel, SeniorMemberLoader, JuniorMemberLoader
import src.services.team.query as tmq
import src.services.user.loader as ul


class Sample2Service(UseCaseService):
    """Sample 2: Multiple loader instances with different parameters."""

    @query
    async def get_teams_with_detail(cls) -> list[Sample2TeamDetail]:
        """Teams with senior members."""
        async with db.async_session() as session:
            teams = await tmq.get_teams(session)
        teams = [Sample2TeamDetail.model_validate(t) for t in teams]
        return await Resolver(loader_params={
            ul.UserByLevelLoader: {"level": 'senior'}
        }).resolve(teams)

    @query
    async def get_teams_with_detail_of_multiple_level(cls) -> list[Sample2TeamDetailMultipleLevel]:
        """Teams with senior and junior members."""
        async with db.async_session() as session:
            teams = await tmq.get_teams(session)
        teams = [Sample2TeamDetailMultipleLevel.model_validate(t) for t in teams]
        return await Resolver(loader_params={
            SeniorMemberLoader: {"level": 'senior'},
            JuniorMemberLoader: {"level": 'junior'},
        }).resolve(teams)
