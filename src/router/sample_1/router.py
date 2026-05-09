from fastapi import APIRouter

from pydantic_resolve.utils.types import get_return_annotation
from .service import Sample1Service

route = APIRouter(tags=['sample_1'], prefix="/sample_1")

@route.get('/users', response_model=get_return_annotation(Sample1Service.get_users))
async def get_users():
    """1.1 return list of user"""
    return await Sample1Service.get_users()


@route.get('/tasks', response_model=get_return_annotation(Sample1Service.get_tasks))
async def get_tasks():
    """1.2 return list of tasks"""
    return await Sample1Service.get_tasks()


@route.get('/tasks-with-detail', response_model=get_return_annotation(Sample1Service.get_tasks_with_detail))
async def get_tasks_with_detail():
    """1.3 return list of tasks(user)"""
    return await Sample1Service.get_tasks_with_detail()


@route.get('/stories-with-detail', response_model=get_return_annotation(Sample1Service.get_stories_with_detail))
async def get_stories_with_detail():
    """1.4 return list of story(task(user))"""
    return await Sample1Service.get_stories_with_detail()


@route.get('/sprints-with-detail', response_model=get_return_annotation(Sample1Service.get_sprints_with_detail))
async def get_sprints_with_detail():
    """1.5 return list of sprint(story(task(user)))"""
    return await Sample1Service.get_sprints_with_detail()


@route.get('/teams-with-detail', response_model=get_return_annotation(Sample1Service.get_teams_with_detail))
async def get_teams_with_detail():
    """1.6 return list of team(sprint(story(task(user))))"""
    return await Sample1Service.get_teams_with_detail()


@route.get('/teams-with-detail2', response_model=get_return_annotation(Sample1Service.get_teams_with_detail_2))
async def get_teams_with_detail_2():
    """1.7 return list of team(sprint(story(task(user))))"""
    return await Sample1Service.get_teams_with_detail_2()
