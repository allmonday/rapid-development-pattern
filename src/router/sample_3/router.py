from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample3Service

route = APIRouter(tags=['sample_3'], prefix="/sample_3")

@route.get('/teams-with-detail', response_model=get_return_annotation(Sample3Service.get_teams_with_detail))
async def get_teams_with_detail():
    """
    1.1 expose (provide) ancestor data to descendant node.
    """
    return await Sample3Service.get_teams_with_detail()
