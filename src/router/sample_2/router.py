from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample2Service

route = APIRouter(tags=['sample_2'], prefix="/sample_2")

@route.get('/teams-with-detail', response_model=get_return_annotation(Sample2Service.get_teams_with_detail))
async def get_teams_with_detail():
    """1.1 teams with senior members"""
    return await Sample2Service.get_teams_with_detail()


@route.get('/teams-with-detail-of-multiple-level', response_model=get_return_annotation(Sample2Service.get_teams_with_detail_of_multiple_level))
async def get_teams_with_detail_of_multiple_level():
    """1.2 teams with senior and junior members"""
    return await Sample2Service.get_teams_with_detail_of_multiple_level()
