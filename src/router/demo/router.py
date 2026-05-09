from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import DemoService, Payload

route = APIRouter(tags=['demo'], prefix="/demo")

@route.post('/stories', response_model=get_return_annotation(DemoService.get_stories))
async def get_stories_with_detail(payload: Payload):
    return await DemoService.get_stories(payload=payload)

@route.get('/stories-1', response_model=get_return_annotation(DemoService.get_stories_1))
async def get_stories_with_detail_1():
    return await DemoService.get_stories_1()

@route.get('/stories-2', response_model=get_return_annotation(DemoService.get_stories_2))
async def get_stories_with_detail_2():
    return await DemoService.get_stories_2()

@route.get('/stories-3', response_model=get_return_annotation(DemoService.get_stories_3))
async def get_stories_with_detail_3():
    return await DemoService.get_stories_3()
