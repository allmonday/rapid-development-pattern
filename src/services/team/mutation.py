from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from .model import Team, TeamUser
from ..sprint.model import Sprint


# Team 自身的 CRUD
async def create_team(session: AsyncSession, name: str) -> Team:
    """创建团队"""
    team = Team(name=name)
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team


async def update_team(session: AsyncSession, id: int, name: Optional[str] = None) -> Optional[Team]:
    """更新团队"""
    result = await session.execute(select(Team).where(Team.id == id))
    team = result.scalar_one_or_none()

    if team:
        if name is not None:
            team.name = name
        await session.commit()
        await session.refresh(team)

    return team


async def delete_team(session: AsyncSession, id: int) -> bool:
    """删除团队"""
    result = await session.execute(delete(Team).where(Team.id == id))
    await session.commit()
    return result.rowcount > 0


# Team 负责管理 Sprint 子实体
async def create_sprint(session: AsyncSession, team_id: int, name: str, status: str = 'planning') -> Sprint:
    """创建 Sprint"""
    sprint = Sprint(team_id=team_id, name=name, status=status)
    session.add(sprint)
    await session.commit()
    await session.refresh(sprint)
    return sprint


async def delete_sprint(session: AsyncSession, id: int) -> bool:
    """删除 Sprint"""
    result = await session.execute(delete(Sprint).where(Sprint.id == id))
    await session.commit()
    return result.rowcount > 0


# 团队成员管理
async def add_team_member(session: AsyncSession, team_id: int, user_id: int) -> bool:
    """添加团队成员"""
    team_user = TeamUser(team_id=team_id, user_id=user_id)
    session.add(team_user)
    await session.commit()
    return True


async def remove_team_member(session: AsyncSession, team_id: int, user_id: int) -> bool:
    """移除团队成员"""
    result = await session.execute(
        delete(TeamUser).where(TeamUser.team_id == team_id, TeamUser.user_id == user_id)
    )
    await session.commit()
    return result.rowcount > 0
