from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample6Service

route = APIRouter(tags=['sample_6'], prefix="/sample_6")

@route.get('/page-info', response_model=get_return_annotation(Sample6Service.get_page_info))
async def get_page_info_6():
    return await Sample6Service.get_page_info()
