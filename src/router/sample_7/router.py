from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample7Service

route = APIRouter(tags=['sample_7'], prefix="/sample_7")

@route.get('/tasks', response_model=get_return_annotation(Sample7Service.get_tasks))
async def get_tasks():
    return await Sample7Service.get_tasks()


@route.get('/user/{id}/stat', response_model=get_return_annotation(Sample7Service.get_user_stat))
async def get_user_stat(id: int):
    return await Sample7Service.get_user_stat(id=id)
