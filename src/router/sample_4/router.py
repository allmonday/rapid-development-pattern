from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample4Service

route = APIRouter(tags=['sample_4'], prefix="/sample_4")

@route.get('/teams-with-detail', response_model=get_return_annotation(Sample4Service.get_teams_with_detail))
async def get_teams_with_detail():
    return await Sample4Service.get_teams_with_detail()
