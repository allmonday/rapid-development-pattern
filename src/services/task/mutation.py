from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from .model import Task


# Task 自身负责更新
async def update_task(
    session: AsyncSession,
    id: int,
    name: Optional[str] = None,
    owner_id: Optional[int] = None,
    estimate: Optional[int] = None
) -> Optional[Task]:
    """更新 Task"""
    result = await session.execute(select(Task).where(Task.id == id))
    task = result.scalar_one_or_none()

    if task:
        if name is not None:
            task.name = name
        if owner_id is not None:
            task.owner_id = owner_id
        if estimate is not None:
            task.estimate = estimate
        await session.commit()
        await session.refresh(task)

    return task
