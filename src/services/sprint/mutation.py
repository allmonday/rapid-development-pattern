from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from .model import Sprint
from ..story.model import Story


# Sprint 自身负责更新
async def update_sprint(
    session: AsyncSession,
    id: int,
    name: Optional[str] = None,
    status: Optional[str] = None
) -> Optional[Sprint]:
    """更新 Sprint"""
    result = await session.execute(select(Sprint).where(Sprint.id == id))
    sprint = result.scalar_one_or_none()

    if sprint:
        if name is not None:
            sprint.name = name
        if status is not None:
            sprint.status = status
        await session.commit()
        await session.refresh(sprint)

    return sprint


# Sprint 负责管理 Story 子实体
async def create_story(session: AsyncSession, sprint_id: int, name: str, owner_id: int) -> Story:
    """创建 Story"""
    story = Story(sprint_id=sprint_id, name=name, owner_id=owner_id)
    session.add(story)
    await session.commit()
    await session.refresh(story)
    return story


async def delete_story(session: AsyncSession, id: int) -> bool:
    """删除 Story"""
    result = await session.execute(delete(Story).where(Story.id == id))
    await session.commit()
    return result.rowcount > 0
