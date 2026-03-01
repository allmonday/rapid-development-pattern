from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from .model import User


async def create_user(session: AsyncSession, name: str, level: str = 'user') -> User:
    """创建用户"""
    user = User(name=name, level=level)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    id: int,
    name: Optional[str] = None,
    level: Optional[str] = None
) -> Optional[User]:
    """更新用户"""
    result = await session.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()

    if user:
        if name is not None:
            user.name = name
        if level is not None:
            user.level = level
        await session.commit()
        await session.refresh(user)

    return user


async def delete_user(session: AsyncSession, id: int) -> bool:
    """删除用户"""
    result = await session.execute(delete(User).where(User.id == id))
    await session.commit()
    return result.rowcount > 0
