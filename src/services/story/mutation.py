from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from .model import Story
from ..task.model import Task


# Story 自身负责更新
async def update_story(
    session: AsyncSession,
    id: int,
    name: Optional[str] = None,
    owner_id: Optional[int] = None
) -> Optional[Story]:
    """更新 Story"""
    result = await session.execute(select(Story).where(Story.id == id))
    story = result.scalar_one_or_none()

    if story:
        if name is not None:
            story.name = name
        if owner_id is not None:
            story.owner_id = owner_id
        await session.commit()
        await session.refresh(story)

    return story


# Story 负责管理 Task 子实体
async def create_task(
    session: AsyncSession,
    story_id: int,
    name: str,
    owner_id: int,
    estimate: int = 0
) -> Task:
    """创建 Task"""
    task = Task(story_id=story_id, name=name, owner_id=owner_id, estimate=estimate)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, id: int) -> bool:
    """删除 Task"""
    result = await session.execute(delete(Task).where(Task.id == id))
    await session.commit()
    return result.rowcount > 0
