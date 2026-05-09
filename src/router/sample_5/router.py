from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample5Service

route = APIRouter(tags=['sample_5'], prefix="/sample_5")

@route.get('/page-info/{team_id}', response_model=get_return_annotation(Sample5Service.get_page_info))
async def get_page_info(team_id: int):
    return await Sample5Service.get_page_info(team_id=team_id)
