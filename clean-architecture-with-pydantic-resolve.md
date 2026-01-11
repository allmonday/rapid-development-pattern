# 基于 Pydantic-Resolve 和 FastAPI-Voyager 的 Clean Architecture 实践

> 一套面向复杂业务场景的 Python Web 开发方法论

## 目录

- [1. 背景与问题](#1-背景与问题)
  - [1.1 当前主流做法及其痛点](#11-当前主流做法及其痛点)
  - [1.2 问题根源分析](#12-问题根源分析)
    - [问题 1：业务模型与数据模型混淆](#问题-1业务模型与数据模型混淆)
    - [问题 2：依赖方向错误](#问题-2依赖方向错误)
    - [问题 3：缺少业务关系的显式声明](#问题-3缺少业务关系的显式声明)
    - [问题 4：中间表的技术暴露](#问题-4中间表的技术暴露)
- [2. Clean Architecture 思想](#2-clean-architecture-思想)
  - [2.1 核心原则](#21-核心原则)
  - [2.2 依赖规则](#22-依赖规则)
  - [2.3 在 Web 开发中的应用](#23-在-web-开发中的应用)
- [3. Pydantic-Resolve：业务模型层](#3-pydantic-resolve业务模型层)
  - [3.1 核心概念](#31-核心概念)
  - [3.2 ERD：业务关系的声明](#32-erd业务关系的声明)
  - [3.3 DataLoader：批量加载的秘密](#33-dataloader批量加载的秘密)
  - [3.4 Resolve 与 Post：数据组装与计算](#34-resolve-与-post数据组装与计算)
  - [3.5 跨层数据传递](#35-跨层数据传递)
- [4. FastAPI-Voyager：架构可视化](#4-fastapi-voyager架构可视化)
  - [4.1 核心功能](#41-核心功能)
  - [4.2 ERD 与 API Route 的结合](#42-erd-与-api-route-的结合)
  - [4.3 实战应用场景](#43-实战应用场景)
- [5. 完整的开发流程](#5-完整的开发流程)
  - [5.1 架构设计阶段](#51-架构设计阶段)
  - [5.2 实体定义阶段](#52-实体定义阶段)
  - [5.3 数据层实现](#53-数据层实现)
  - [5.4 API 实现阶段](#54-api-实现阶段)
  - [5.5 可视化验证](#55-可视化验证)
- [6. 与其他方案的对比](#6-与其他方案的对比)
  - [6.1 vs 传统 ORM](#61-vs-传统-orm)
  - [6.2 vs GraphQL](#62-vs-graphql)
  - [6.3 vs DDD 框架](#63-vs-ddd-框架)
- [7. 总结](#7-总结)

---

## 1. 背景与问题

### 1.1 当前主流做法及其痛点

在 Python Web 开发中，处理复杂业务场景时，开发者通常采用以下几种模式：

#### 模式一：直接使用 ORM（如 SQLAlchemy）

```python
@router.get("/teams/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # 获取团队基本信息
    team = await session.get(Team, team_id)

    # 获取 Sprint 列表
    sprints = await session.execute(
        select(Sprint).where(Sprint.team_id == team_id)
    )
    team.sprints = sprints.scalars().all()

    # 获取每个 Sprint 的 Story
    for sprint in team.sprints:
        stories = await session.execute(
            select(Story).where(Story.sprint_id == sprint.id)
        )
        sprint.stories = stories.scalars().all()

        # 获取每个 Story 的 Task
        for story in sprint.stories:
            tasks = await session.execute(
                select(Task).where(Task.story_id == story.id)
            )
            story.tasks = tasks.scalars().all()

            # 获取每个 Task 的负责人
            for task in story.tasks:
                task.owner = await session.get(User, task.owner_id)

    return team
```

**优点**：
- 简单直接，容易上手
- 与数据库表结构一一对应
- ORM 提供了类型安全

**缺点**：

- **N+1 查询问题**：产生了大量的数据库查询
- **命令式代码**：数据获取逻辑散落在循环中
- **难以维护**：业务逻辑与数据获取逻辑混杂
- **性能不可控**：查询效率随数据量下降
- **代码重复**：类似的数据获取逻辑在多个 API 中重复

#### 模式二：使用 ORM 的 Eager Loading

```python
@router.get("/teams/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # 使用 joinedload 预加载关联数据
    result = await session.execute(
        select(Team)
        .options(
            joinedload(Team.sprints)
            .joinedload(Sprint.stories)
            .joinedload(Story.tasks)
            .joinedload(Task.owner)
        )
        .where(Team.id == team_id)
    )
    return result.scalar_one()
```

**优点**：
- 解决了 N+1 查询问题（使用 JOIN）
- 代码更简洁

**缺点**：

- **笛卡尔积问题**：多层 JOIN 导致数据量爆炸
- **灵活性差**：无法根据需求选择性加载
- **过度获取**：前端不需要的数据也被加载
- **配置复杂**：需要理解 `lazy`, `joinedload`, `subquery` 等概念
- **一刀切**：所有 API 使用相同的加载策略

#### 模式三：手动组装数据

```python
@router.get("/teams/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # 1. 批量获取所有需要的数据
    team = await session.get(Team, team_id)

    sprints_result = await session.execute(
        select(Sprint).where(Sprint.team_id == team_id)
    )
    sprint_ids = [s.id for s in sprints_result.scalars().all()]

    stories_result = await session.execute(
        select(Story).where(Story.sprint_id.in_(sprint_ids))
    )
    story_ids = [s.id for s in stories_result.scalars().all()]

    tasks_result = await session.execute(
        select(Task).where(Story.id.in_(story_ids))
    )
    tasks = tasks_result.scalars().all()

    owner_ids = list(set(t.owner_id for t in tasks))
    owners_result = await session.execute(
        select(User).where(User.id.in_(owner_ids))
    )
    owners = {u.id: u for u in owners_result.scalars().all()}

    # 2. 手动组装数据结构
    sprint_dict = {s.id: s for s in sprints_result.scalars().all()}
    story_dict = {s.id: s for s in stories_result.scalars().all()}

    for story in story_dict.values():
        story.tasks = [t for t in tasks if t.story_id == story.id]
        for task in story.tasks:
            task.owner = owners.get(task.owner_id)

    for sprint in sprint_dict.values():
        sprint.stories = [s for s in story_dict.values() if s.sprint_id == sprint.id]

    team.sprints = list(sprint_dict.values())

    return team
```

**优点**：
- 性能最优（完全控制查询）
- 没有冗余数据

**缺点**：

- **代码冗长**：需要编写大量组装逻辑
- **容易出错**：手动组装容易产生 bug
- **难以维护**：业务变更时需要修改多处
- **重复劳动**：类似逻辑在多个 API 中重复
- **丢失了业务语义**：代码变成"数据搬运"，看不出业务意图

#### 模式四：使用 GraphQL

```python
type Query {
    team(id: ID!): Team
}

type Team {
    id: ID!
    name: String!
    sprints: [Sprint!]!
}

type Sprint {
    id: ID!
    name: String!
    stories: [Story!]!
}

type Story {
    id: ID!
    name: String!
    tasks: [Task!]!
}

type Task {
    id: ID!
    name: String!
    owner: User!
}
```

**优点**：
- 前端按需获取数据
- 类型安全
- 自动解决 N+1 查询（使用 DataLoader）

**缺点**：

- **学习曲线陡峭**：需要学习 Schema、Resolver、DataLoader 等概念
- **过度灵活**：前端可以构造任意查询，难以优化
- **调试困难**：问题定位比 REST API 复杂
- **集成复杂**：需要额外的服务器和工具链
- **与现有生态不兼容**：无法直接使用 FastAPI 的依赖注入等特性
- **ERD 和用例界限模糊**：GraphQL Schema 同时扮演实体模型和查询接口的角色，导致：
  - 难以区分业务实体（ERD）和用例（Query/Mutation）
  - 最佳实践不清晰：应该按实体设计还是按用例设计？
  - Schema 膨胀：所有用例都在同一个 Schema 中，难以组织
  - 权限控制困难：不同用例对同一实体的访问权限难以管理

### 1.2 问题根源分析

以上所有模式的核心问题在于：

#### 问题 1：业务模型与数据模型混淆 {#问题-1业务模型与数据模型混淆}

```python
# SQLAlchemy ORM 同时扮演两个角色：
# 1. 数据模型（如何存储）
# 2. 业务模型（业务概念）

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # 这是数据库的外键关系，还是业务关系？
    sprints = relationship("Sprint", back_populates="team")
```

**问题**：
- 数据库的设计约束（如外键、级联）影响了业务建模
- 业务概念被数据库结构限制
- 无法表达跨库、跨服务的业务关系

#### 问题 2：依赖方向错误 {#问题-2依赖方向错误}

```
传统架构的依赖方向：
┌─────────────┐
│   API Layer │  ← 依赖于
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ ORM Models  │  ← 依赖于
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Database   │
└─────────────┘

问题：业务规则依赖于数据库实现！
```

**违反了 Clean Architecture 的依赖规则**：
- 业务规则应该是最稳定的核心
- 数据库是实现细节，应该依赖业务规则
- 当数据库变化时，业务规则不应该受影响

#### 问题 3：缺少业务关系的显式声明 {#问题-3缺少业务关系的显式声明}

```python
# 传统方式：业务关系隐藏在查询中
async def get_team_tasks(team_id: int):
    # "团队的任务"这个业务概念隐藏在 SQL WHERE 中
    result = await session.execute(
        select(Task)
        .join(Sprint, Sprint.id == Task.sprint_id)
        .where(Sprint.team_id == team_id)
    )
    return result.scalars().all()
```

**问题**：
- 业务关系没有显式声明
- 新成员难以理解业务模型
- 无法自动检查一致性
- 重构时容易破坏业务逻辑

#### 问题 4：中间表的技术暴露 {#问题-4中间表的技术暴露}

在 SQLAlchemy ORM 中，多对多关系需要显式定义中间表，这导致技术细节泄漏到业务层。

```python
# SQLAlchemy ORM：必须定义中间表
class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # ORM relationship 需要指定中间表
    members = relationship("User",
                          secondary="team_members",  # 必须指定中间表
                          back_populates="teams")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    teams = relationship("Team",
                        secondary="team_members",  # 必须指定中间表
                        back_populates="members")

# 中间表（技术实现细节）
class TeamMember(Base):
    __tablename__ = 'team_members'
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String)  # 可能还有额外字段

# 查询时需要关心中间表的存在
@router.get("/teams/{team_id}")
async def get_team_members(team_id: int, session: AsyncSession):
    # 必须通过中间表查询
    result = await session.execute(
        select(User)
        .join(TeamMember, TeamMember.user_id == User.id)  # 中间表暴露
        .where(TeamMember.team_id == team_id)
    )
    return result.scalars().all()
```

**问题**：

1. **技术细节泄漏**：
   - 业务代码必须知道 `team_members` 中间表的存在
   - 查询逻辑需要 join 中间表，增加了复杂度

2. **业务语义模糊**：
   - `TeamMember` 是业务概念还是纯技术实现？
   - 如果中间表有额外字段（如 `role`、`joined_at`），是否应该建模为实体？

3. **数据组装复杂**：
   - 查询"团队的所有成员"需要 join 中间表
   - 查询"用户所属的团队"也需要 join 中间表
   - 业务逻辑被数据库结构绑架

**对比：Pydantic-Resolve ERD 的方式**

```python
# ERD：业务概念清晰，无需关心中间表
class TeamEntity(BaseModel, BaseEntity):
    """团队实体 - 业务概念"""
    __relationships__ = [
        # 直接表达"团队有多个成员"的业务关系
        Relationship(
            field='id',
            target_kls=list[UserEntity],
            loader=team_to_users_loader  # loader 内部处理中间表
        ),
    ]
    id: int
    name: str

class UserEntity(BaseModel, BaseEntity):
    """用户实体 - 业务概念"""
    __relationships__ = [
        # 直接表达"用户属于多个团队"的业务关系
        Relationship(
            field='id',
            target_kls=list[TeamEntity],
            loader=user_to_teams_loader
        ),
    ]
    id: int
    name: str

# Loader 实现细节：中间表只在这里出现
async def team_to_users_loader(team_ids: list[int]):
    """加载团队成员 - 内部处理中间表"""
    async with get_session() as session:
        # 只有这里需要知道中间表的存在
        result = await session.execute(
            select(User)
            .join(TeamMember, TeamMember.user_id == User.id)
            .where(TeamMember.team_id.in_(team_ids))
        )
        users = result.scalars().all()

        # 构建映射
        users_by_team = {}
        for user in users:
            for tm in user.team_memberships:
                if tm.team_id not in users_by_team:
                    users_by_team[tm.team_id] = []
                users_by_team[tm.team_id].append(user)

        return [users_by_team.get(tid, []) for tid in team_ids]
```

**关键差异**：

| 维度 | SQLAlchemy ORM | Pydantic-Resolve ERD |
|------|----------------|---------------------|
| **中间表位置** | 暴露在业务层 | 隐藏在 loader 实现中 |
| **业务语义** | 技术关系 (`secondary`) | 业务关系 (`团队包含成员`) |
| **查询代码** | 需要 join 中间表 | `loader.load(team_id)` |
| **代码位置** | 分散在多处 | 集中在 loader |
| **测试** | 依赖数据库表结构 | 可 mock loader |

**架构优势**：

```
传统方式：
Team → TeamMember (中间表) → User
业务层需要知道中间表的存在

Pydantic-Resolve 方式：
Team → User (业务关系)
中间表是数据层的实现细节，业务层不关心
```

这意味着：

1. **业务模型纯净**：Team 和 User 的关系直接表达业务语义
2. **技术细节封装**：中间表的存在被封装在 loader 中
3. **灵活的存储策略**：
   - 数据库可以用中间表实现
   - 也可以用 JSON 字段存储
   - 甚至可以是外部服务（如 LDAP）
   - 业务层代码无需修改

4. **易于理解**：新人看到 ERD 就能理解业务关系，不需要先学习数据库设计

---

## 2. Clean Architecture 思想

### 2.1 核心原则

Clean Architecture 由 Robert C. Martin (Uncle Bob) 提出，核心思想是：

> **"Software architecture is the art of drawing lines that I call boundaries."**
> **软件架构的艺术在于画界线。**

#### 原则 1：依赖规则

```
外层依赖内层，内层不依赖外层。

                ↓ 依赖方向
    ┌─────────────────────┐
    │   Frameworks &      │  外层
    │   Drivers           │  (实现细节)
    ├─────────────────────┤
    │   Interface         │
    │   Adapters          │
    ├─────────────────────┤
    │   Use Cases         │
    │   (Application)     │
    ├─────────────────────┤
    │   Entities          │  内层
    │   (Business Rules)  │  (核心)
    └─────────────────────┘
```

**关键点**：
- 内层不知道外层的存在
- 内层不包含外层的信息（如数据库、框架、UI）
- 外层的实现可以替换而不影响内层

#### 原则 2：业务规则独立

```python
# ❌ 错误：业务规则依赖数据库
class Task:
    def calculate_priority(self, session):
        # 业务逻辑被数据库实现细节污染
        if self.assignee_id in session.query(TeamMember).filter_by(role='lead'):
            return 'high'

# ✅ 正确：业务规则独立
class Task:
    def calculate_priority(self, assignee_roles):
        # 业务逻辑只依赖业务概念
        if 'lead' in assignee_roles:
            return 'high'
```

#### 原则 3：跨边界的数据传递

```python
# 内层定义数据结构
class TaskEntity(BaseModel):
    id: int
    name: str
    assignee_id: int

# 外层负责转换
def task_entity_to_orm(entity: TaskEntity) -> Task:
    return Task(
        id=entity.id,
        name=entity.name,
        assignee_id=entity.assignee_id
    )
```

### 2.2 依赖规则

在 Web 开发中，依赖规则可以这样理解：

```
┌──────────────────────────────────────────────────────────┐
│              Presentation Layer (外层)                    │
│  - FastAPI Routes                                        │
│  - Request/Response Models                               │
│  - 依赖: Application Layer                                │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│            Application Layer (Use Cases)                 │
│  - 业务用例（获取用户、创建订单）                          │
│  - 依赖: Domain Layer                                     │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│               Domain Layer (内层)                        │
│  - Entities (业务实体)                                    │
│  - Business Rules (业务规则)                              │
│  - Value Objects (值对象)                                 │
│  - 不依赖任何外层                                          │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│            Infrastructure Layer (最外层)                 │
│  - Database (SQLAlchemy)                                 │
│  - External Services                                     │
│  - File System                                           │
└──────────────────────────────────────────────────────────┘
```

**关键洞察**：
- **Entities 不应该知道 SQLAlchemy 的存在**
- **Business Rules 不应该知道数据库表结构**
- **Use Cases 不应该知道 HTTP 协议的细节**

### 2.3 在 Web 开发中的应用

#### 传统架构的问题

```python
# 传统方式：所有层次耦合

# Domain Layer (应该独立，但实际上依赖了 ORM)
class User(Base):  # ← SQLAlchemy Base
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

# Application Layer (应该只依赖 Domain，但直接使用了 ORM)
async def create_user(data: dict, session: AsyncSession):
    user = User(**data)  # ← 直接使用 ORM Model
    session.add(user)
    await session.commit()

# Presentation Layer
@router.post("/users")
async def api_create_user(data: dict, session=Depends(get_session)):
    return await create_user(data, session)  # ← 暴露了数据库细节
```

**问题**：
1. Domain Layer 被 SQLAlchemy 绑定
2. 业务逻辑无法脱离数据库测试
3. 切换数据库（如 PostgreSQL → MongoDB）需要修改所有层

#### Clean Architecture 的做法

```python
# Domain Layer (完全独立)
class UserEntity(BaseModel):
    """业务实体 - 不依赖任何框架"""
    id: int
    name: str
    email: str

    def validate_email(self):
        """业务规则"""
        if '@' not in self.email:
            raise ValueError('Invalid email')

# Application Layer (只依赖 Domain)
async def create_user_use_case(data: dict, user_repository):
    """用例 - 只依赖业务概念"""
    user = UserEntity(**data)
    user.validate_email()
    await user_repository.save(user)

# Interface Adapter (Repository 接口)
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: UserEntity): ...

# Infrastructure Layer (具体实现)
class SqlUserRepository(UserRepository):
    async def save(self, user: UserEntity):
        # 将 UserEntity 转换为 ORM Model
        orm_user = UserORM(**user.model_dump())
        self.session.add(orm_user)
        await self.session.commit()

# Presentation Layer
@router.post("/users", response_model=UserResponse)
async def api_create_user(
    data: UserCreateRequest,
    user_repo=Depends(get_user_repository)
):
    user = await create_user_use_case(data.model_dump(), user_repo)
    return user
```

**优势**：

1. Domain Layer 完全独立，可以单独测试
2. 业务逻辑不依赖数据库
3. 可以轻松切换数据库实现
4. 依赖方向正确：外层依赖内层

---

## 3. Pydantic-Resolve：业务模型层

### 3.1 核心概念

Pydantic-Resolve 是一个基于 Pydantic 的数据组装工具，让你可以用**声明式**的方式构建复杂的数据结构。

#### 核心思想

> **"描述你想要什么，而不是如何获取"**

```python
# ❌ 命令式：如何获取
async def get_teams_with_tasks():
    teams = await get_teams()
    for team in teams:
        team.tasks = await get_tasks_by_team(team.id)  # N+1 问题
        for task in team.tasks:
            task.owner = await get_user(task.owner_id)  # 又是 N+1
    return teams

# ✅ 声明式：想要什么
class TeamResponse(BaseModel):
    id: int
    name: str

    tasks: list[TaskResponse] = []
    def resolve_tasks(self, loader=Loader(team_to_tasks_loader)):
        return loader.load(self.id)

class TaskResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    owner: Optional[UserResponse] = None
    def resolve_owner(self, loader=Loader(user_loader)):
        return loader.load(self.owner_id)

# 使用
teams = await query_teams_from_db()
result = await Resolver().resolve(teams)
```

**关键差异**：
- 命令式：关注"如何获取"（how）
- 声明式：关注"想要什么"（what）

### 3.2 ERD：业务关系的声明

#### 定义实体关系图

```python
from pydantic_resolve import base_entity, Relationship, config_global_resolver

# 1. 创建 BaseEntity
BaseEntity = base_entity()

# 2. 定义业务实体
class UserEntity(BaseModel, BaseEntity):
    """用户实体 - 业务概念"""
    __relationships__ = [
        # 关系1：用户拥有的任务（作为创建者）
        Relationship(
            field='id',
            target_kls=list[TaskEntity],
            loader=user_to_created_tasks_loader
        ),
        # 关系2：用户负责的任务（作为执行者）
        Relationship(
            field='id',
            target_kls=list[TaskEntity],
            loader=user_to_assigned_tasks_loader
        ),
        # 关系3：用户所属的团队
        Relationship(
            field='id',
            target_kls=list[TeamEntity],
            loader=user_to_teams_loader
        ),
    ]

    id: int
    name: str
    email: str

class TaskEntity(BaseModel, BaseEntity):
    """任务实体 - 业务概念"""
    __relationships__ = [
        Relationship(
            field='story_id',
            target_kls=StoryEntity,
            loader=story_loader
        ),
        Relationship(
            field='owner_id',
            target_kls=UserEntity,
            loader=user_loader
        ),
    ]

    id: int
    name: str
    story_id: int
    owner_id: int
    estimate: int

# 3. 注册 ERD
diagram = BaseEntity.get_diagram()
config_global_resolver(diagram)
```

#### ERD 的关键特性

**1. 业务语义优先**

```python
# ERD 表达的是业务概念，不是数据库约束
class TeamEntity(BaseModel, BaseEntity):
    __relationships__ = [
        # 团队有多个 Sprint（业务关系）
        Relationship(field='id', target_kls=list[SprintEntity], loader=...),
        # 团队有多个成员（业务关系，可能通过中间表实现）
        Relationship(field='id', target_kls=list[UserEntity], loader=...),
        # 团队有多个任务（业务关系，可能通过 Sprint 间接关联）
        Relationship(field='id', target_kls=list[TaskEntity], loader=...),
    ]
```

**2. 同一字段的多个关系**

当同一个字段需要建立到相同目标类型的多个关系时，使用 `MultipleRelationship`：

```python
from pydantic_resolve import MultipleRelationship, Link

class UserEntity(BaseModel, BaseEntity):
    """用户实体 - 一个用户可以有多种方式与任务关联"""
    __relationships__ = [
        # 同一个字段 'id'，到同一个目标类型的多个业务关系
        MultipleRelationship(
            field='id',
            target_kls=list[TaskEntity],
            links=[
                Link(biz='created', loader=created_tasks_loader),
                Link(biz='assigned', loader=assigned_tasks_loader),
                Link(biz='reviewed', loader=reviewed_tasks_loader),
            ]
        ),
    ]
    id: int
    name: str

# 在 Response 中使用 LoadBy 区分不同的关系
class UserWithCreatedTasksResponse(BaseModel):
    id: int
    name: str

    # 使用 biz_name 参数指定要加载的关系
    created_tasks: Annotated[list[TaskResponse], LoadBy('id', biz='created')] = []

class UserWithAssignedTasksResponse(BaseModel):
    id: int
    name: str

    assigned_tasks: Annotated[list[TaskResponse], LoadBy('id', biz='assigned')] = []
```

**3. 虚拟关系（脱离数据库的业务关系）**

pydantic-resolve ERD 的强大之处在于：**业务关系不限于数据库外键**。可以从任何数据源加载关联数据，包括 RPC 服务、本地文件、外部 API 等。

```python
from pydantic_resolve import base_entity, Relationship

BaseEntity = base_entity()

# 示例 1：从外部 RPC 服务加载用户头像
class UserEntity(BaseModel, BaseEntity):
    """用户实体"""
    __relationships__ = [
        # 关系1：从数据库加载的任务（标准关系）
        Relationship(
            field='id',
            target_kls=list[TaskEntity],
            loader=user_to_tasks_loader  # 从数据库加载
        ),
        # 关系2：从文件系统加载的配置（虚拟关系）
        Relationship(
            field='id',
            target_kls=UserConfigEntity,
            loader=user_config_from_file_loader  # 从 JSON/YAML 文件加载
        ),
        # 关系3：从 RPC 服务加载的用户画像（虚拟关系）
        Relationship(
            field='id',
            target_kls=UserProfileEntity,
            loader=user_profile_from_rpc_loader  # 从 gRPC/HTTP RPC 服务加载
        ),
    ]
    id: int
    name: str
    email: str

class UserConfigEntity(BaseModel):
    """用户配置 - 来自文件系统"""
    theme: str
    language: str
    notifications_enabled: bool

class UserProfileEntity(BaseModel):
    """用户画像 - 来自外部服务"""
    interests: list[str]
    skills: list[str]
    reputation_score: float

# Loader 实现：从文件系统加载配置
async def user_config_from_file_loader(user_ids: list[int]) -> list[UserConfigEntity]:
    """从本地 JSON 文件加载用户配置"""
    configs = []
    for user_id in user_ids:
        # 从文件系统读取配置文件
        config_path = f"/data/users/{user_id}/config.json"
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                configs.append(UserConfigEntity(**config_data))
        except FileNotFoundError:
            # 配置文件不存在，返回默认配置
            configs.append(UserConfigEntity(
                theme='light',
                language='en',
                notifications_enabled=True
            ))
    return configs

# Loader 实现：从 RPC 服务加载用户画像
async def user_profile_from_rpc_loader(user_ids: list[int]) -> list[UserProfileEntity]:
    """从外部 gRPC 服务加载用户画像"""
    # 批量调用外部 RPC 服务
    async with UserProfileServiceClient() as client:
        # 假设 RPC 服务支持批量查询
        request = GetBatchUserProfilesRequest(user_ids=user_ids)
        response = await client.get_batch_profiles(request)

        # 转换为实体
        profiles = [
            UserProfileEntity(
                interests=p.interests,
                skills=p.skills,
                reputation_score=p.reputation_score
            )
            for p in response.profiles
        ]
        return profiles

# 示例 2：从消息队列获取实时状态
class OrderEntity(BaseModel, BaseEntity):
    """订单实体"""
    __relationships__ = [
        # 从数据库查询订单历史
        Relationship(
            field='id',
            target_kls=list[PaymentEntity],
            loader=order_to_payments_loader
        ),
        # 从 Redis（缓存/消息队列）获取实时状态
        Relationship(
            field='id',
            target_kls=OrderStatusEntity,
            loader=order_status_from_redis_loader  # 从 Redis 获取实时状态
        ),
    ]
    id: int
    order_number: str

class OrderStatusEntity(BaseModel):
    """订单实时状态 - 来自 Redis"""
    status: str
    progress: int
    estimated_delivery: datetime
    last_updated: datetime

async def order_status_from_redis_loader(order_ids: list[int]) -> list[OrderStatusEntity]:
    """从 Redis 获取订单实时状态"""
    # 批量从 Redis 读取
    import redis.asyncio as redis

    redis_client = await redis.Redis(host='localhost', port=6379, db=0)
    statuses = []

    for order_id in order_ids:
        # 从 Redis Hash 读取状态
        status_key = f"order:status:{order_id}"
        status_data = await redis_client.hgetall(status_key)

        if status_data:
            statuses.append(OrderStatusEntity(
                status=status_data[b'status'].decode(),
                progress=int(status_data[b'progress'].decode()),
                estimated_delivery=datetime.fromisoformat(status_data[b'estimated_delivery'].decode()),
                last_updated=datetime.fromisoformat(status_data[b'last_updated'].decode())
            ))
        else:
            # Redis 中没有数据，返回默认状态
            statuses.append(OrderStatusEntity(
                status='pending',
                progress=0,
                estimated_delivery=None,
                last_updated=datetime.now()
            ))

    return statuses
```

**核心优势**：

1. **数据源无关性**：
   - 关系定义不关心数据从哪里来
   - 可以是数据库、文件系统、RPC 服务、消息队列、外部 API
   - 业务逻辑保持一致

2. **混合数据源**：
   ```
   UserEntity
     ├── tasks (数据库)
     ├── config (本地文件)
     └── profile (RPC 服务)

   一个实体的关联数据来自多个不同的数据源
   ```

3. **技术解耦**：
   - 更换数据源只需修改 loader 实现
   - ERD 定义和业务逻辑无需修改
   - 例如：从本地配置文件迁移到配置中心（etcd/Consul）

4. **性能优化**：
   - 热点数据放 Redis
   - 大文件计算结果放对象存储
   - 实时状态从消息队列订阅
   - 根据业务需求选择最合适的存储

**与传统 ORM 的对比**：

| 维度 | 传统 ORM (SQLAlchemy) | Pydantic-Resolve ERD |
|------|----------------------|---------------------|
| **数据源** | 仅限数据库 | 任何数据源 |
| **关系定义** | `relationship()` + 外键 | `Relationship()` + loader |
| **跨服务查询** | 需要手动调用 API | 无缝集成，就像本地查询 |
| **混合数据源** | 困难 | 天然支持 |
| **测试** | 需要数据库 | 可 mock loader |

**实际应用场景**：

```python
# 电商订单系统
class OrderEntity(BaseModel, BaseEntity):
    __relationships__ = [
        # 从 PostgreSQL 查询订单基本信息
        Relationship(field='id', target_k=list[OrderItemEntity], loader=items_loader),
        # 从 Redis 获取物流实时状态
        Relationship(field='id', target_kls=LogisticsStatusEntity, loader=redis_status_loader),
        # 从对象存储（S3）获取发票 PDF
        Relationship(field='id', target_kls=InvoiceEntity, loader=s3_invoice_loader),
        # 从推荐服务获取相关商品
        Relationship(field='user_id', target_kls=list[ProductEntity], loader=recommendation_loader),
    ]

# 微服务架构
class ProductEntity(BaseModel, BaseEntity):
    __relationships__ = [
        # 从库存服务查询库存
        Relationship(field='id', target_kls=InventoryEntity, loader=inventory_rpc_loader),
        # 从评论服务查询评论
        Relationship(field='id', target_kls=list[ReviewEntity], loader=review_rpc_loader),
        # 从价格服务查询促销价格
        Relationship(field='id', target_kls=PriceEntity, loader=pricing_rpc_loader),
    ]
```

这就是 pydantic-resolve ERD 的核心价值：**业务关系是业务概念，不应该被技术实现（数据库）所限制**。

### 3.3 DataLoader：批量加载的秘密

#### 问题：N+1 查询

```python
# 传统的逐个加载（N+1 问题）
tasks = [Task(1), Task(2), Task(3), ...]
for task in tasks:
    task.owner = await get_user(task.owner_id)  # N 次查询

# 执行的 SQL：
# SELECT * FROM users WHERE id = 1
# SELECT * FROM users WHERE id = 2
# SELECT * FROM users WHERE id = 3
# ...
```

#### 解决方案：DataLoader

```python
from aiodataloader import DataLoader
from pydantic_resolve import build_list

class UserLoader(DataLoader):
    async def batch_load_fn(self, user_ids: list[int]):
        # 1. 批量查询（1 次查询）
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id.in_(user_ids))
            )
            users = result.scalars().all()

        # 2. 构建映射：user_id -> User
        return build_list(users, user_ids, lambda u: u.id)

# 使用
loader = UserLoader()
tasks = [Task(1), Task(2), Task(3), ...]
for task in tasks:
    task.owner = await loader.load(task.owner_id)  # 自动批量

# 执行的 SQL：
# SELECT * FROM users WHERE id IN (1, 2, 3, ...)  # 只有 1 次查询！
```

#### 工作原理

```
请求序列：
1. load(1) → 缓存等待
2. load(2) → 缓存等待
3. load(3) → 缓存等待
4. load(1) → 命中缓存，立即返回
5. 事件循环触发 → batch_load_fn([1, 2, 3])
6. 结果分配给等待的 Promise
```

**关键特性**：
- **批量**：自动将单个请求合并成批量请求
- **缓存**：同一个 ID 只查询一次
- **并发**：利用事件循环自动调度

### 3.4 Resolve 与 Post：数据组装与计算

#### Resolve：声明数据依赖

```python
class TaskResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    # resolve: 通过 DataLoader 加载
    owner: Optional[UserResponse] = None
    def resolve_owner(self, loader=Loader(user_batch_loader)):
        return loader.load(self.owner_id)
```

**工作流程**：

1. Resolver 扫描所有 `resolve_{field}` 方法
2. 收集所有需要加载的 `owner_id`
3. 批量调用 `user_batch_loader`
4. 将结果填充到 `owner` 字段

#### Post：数据后处理

```python
class StoryResponse(BaseModel):
    id: int
    name: str

    tasks: list[TaskResponse] = []
    def resolve_tasks(self, loader=Loader(story_to_tasks_loader)):
        return loader.load(self.id)

    # post: 在 tasks 加载完成后计算
    total_estimate: int = 0
    def post_total_estimate(self):
        return sum(t.estimate for t in self.tasks)

    completed_count: int = 0
    def post_completed_count(self):
        return sum(1 for t in self.tasks if t.status == 'done')
```

**执行顺序**：
```
1. 执行所有 resolve 方法（并行）
2. 等待所有异步操作完成
3. 执行所有 post 方法（串行）
```

### 3.5 跨层数据传递

#### Expose：父节点向子节点暴露数据

```python
from pydantic_resolve import ExposeAs

class StoryResponse(BaseModel):
    id: int
    name: Annotated[str, ExposeAs('story_name')]  # 暴露给子节点

    tasks: list[TaskResponse] = []

class TaskResponse(BaseModel):
    id: int
    name: str

    # post 方法可以访问祖先节点暴露的数据
    full_name: str = ""
    def post_full_name(self, ancestor_context):
        story_name = ancestor_context.get('story_name')
        return f"{story_name} - {self.name}"
```

**数据流**：
```
Story (story_name: "Sprint 1")
  └─ Task (name: "Fix bug")
      └─ full_name: "Sprint 1 - Fix bug"
```

#### Collect：子节点向父节点收集数据

```python
from pydantic_resolve import Collector, SendTo

class TaskResponse(BaseModel):
    id: int
    owner_id: int

    # 加载 owner，并发送到父节点的收集器
    owner: Annotated[
        Optional[UserResponse],
        LoadBy('owner_id'),
        SendTo('related_users')  # 发送到收集器
    ] = None

class StoryResponse(BaseModel):
    id: int
    name: str

    tasks: list[TaskResponse] = []

    # 收集所有子节点的 owner
    related_users: list[UserResponse] = []
    def post_related_users(self, collector=Collector(alias='related_users')):
        return collector.values()
```

**数据流**：
```
Story
  ├─ Task 1 (owner: Alice)
  ├─ Task 2 (owner: Bob)
  └─ Task 3 (owner: Alice)  ← 去重

Story.related_users: [Alice, Bob]
```

---

## 4. FastAPI-Voyager：架构可视化

### 4.1 核心功能

FastAPI-Voyager 是一个将 FastAPI 应用的架构可视化的工具，它能够：

#### 1. 自动扫描 API 结构

```python
from fastapi import FastAPI
from fastapi_voyager import create_voyager

app = FastAPI()

# 自动扫描所有路由
voyager_app = create_voyager(
    app,
    enable_pydantic_resolve_meta=True  # 显示 pydantic-resolve 元数据
)

app.mount("/voyager", voyager_app)
```

访问 `http://localhost:8000/voyager` 查看可视化。

#### 2. 三层架构展示

```
┌────────────────────────────────────────┐
│  Tag Layer (用例分组)                   │
│  ┌────────┐  ┌────────┐  ┌────────┐   │
│  | users  |  | teams  |  | tasks  |   │
│  └────┬───┘  └────┬───┘  └────┬───┘   │
└───────┼────────────┼────────────┼──────┘
        │            │            │
        ↓            ↓            ↓
┌────────────────────────────────────────┐
│  Route Layer (接口层)                   │
│  ┌────────────┐  ┌────────────┐       │
│  | GET /users |  | POST /teams|       │
│  └──────┬─────┘  └──────┬─────┘       │
└─────────┼────────────────┼─────────────┘
          │                │
          ↓                ↓
┌────────────────────────────────────────┐
│  Schema Layer (业务模型层)              │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  | User |←─| Team |→─| Task |         │
│  └──────┘  └──────┘  └──────┘         │
└────────────────────────────────────────┘
```

### 4.2 ERD 与 API Route 的结合

#### 核心：业务-技术映射图

```python
# 1. 定义 ERD
diagram = ErDiagram(configs=[
    Entity(
        kls=UserEntity,
        relationships=[
            Relationship(field='id', target_kls=list[TaskEntity], loader=...),
            Relationship(field='id', target_kls=list[TeamEntity], loader=...),
        ]
    ),
    Entity(
        kls=TeamEntity,
        relationships=[
            Relationship(field='id', target_kls=list[UserEntity], loader=...),
            Relationship(field='id', target_kls=list[SprintEntity], loader=...),
        ]
    ),
])

# 2. 集成到 Voyager
voyager_app = create_voyager(
    app,
    er_diagram=diagram,  # ← ERD 与 API 结合
    enable_pydantic_resolve_meta=True
)
```

**可视化效果**：

```
API Route (GET /users/{user_id})
    ↓ 返回
UserResponse
    ├─ owner: LoadBy('owner_id') ────→ UserEntity (绿色)
    ├─ tasks: LoadBy('id') ──────────→ list[TaskEntity] (绿色)
    │   └─ owner: LoadBy('owner_id') ─→ UserEntity (绿色)
    └─ total_tasks: post_total_tasks() (蓝色)

ERD 显示的实体关系：
UserEntity ──────────→ TaskEntity
   │                     │
   └─────────────────────┘
```

#### 颜色编码

pydantic-resolve 的操作用不同颜色标记：

- **resolve** (绿色)：通过 DataLoader 加载的数据
- **post** (蓝色)：后处理计算的字段
- **expose as** (紫色)：向后代节点暴露的字段
- **send to** (红色)：发送到父节点收集器的字段
- **collectors** (黑色)：从子节点收集数据的字段

### 4.3 实战应用场景

#### 场景 1：发现架构偏离

```python
# ERD 定义
class UserEntity(BaseModel, BaseEntity):
    __relationships__ = [
        Relationship(field='id', target_kls=list[TaskEntity], loader=...),
    ]

# API 实现（问题）
@router.get("/users/{user_id}", response_model=UserWithProfileResponse)
async def get_user(user_id: int):
    """
    UserWithProfileResponse 包含了 Profile
    但 ERD 中没有定义 User → Profile 的关系
    """
    ...
```

**在 Voyager 中**：
- 点击 `get_user` route
- 看到它返回 `UserWithProfileResponse`
- ERD 图中没有 `User → Profile` 的链接
- **发现问题**：API 实现偏离了业务模型

#### 场景 2：发现过度嵌套

```python
@router.get("/teams/{team_id}", response_model=TeamDetailResponse)
async def get_team(team_id: int):
    """
    返回结构：Team → Sprints → Stories → Tasks → Owner
    嵌套层级太深
    """
    ...
```

**在 Voyager 中**：
- 点击 `get_team` route
- 看到一条很长的依赖链
- 链路的长度直观反映嵌套深度
- **发现问题**：应该拆分 API 或使用字段选择

#### 场景 3：新人快速理解系统

```
传统方式：
1. 阅读几百页的文档
2. 查看散落在各处的代码
3. 问老员工

使用 Voyager：
1. 打开 /voyager
2. 点击感兴趣的 API
3. 看到依赖的模型和关系
4. 5分钟理解核心业务流程
```

---

## 5. 完整的开发流程

### 5.1 架构设计阶段

#### 步骤 1：识别核心业务实体

```markdown
问题域：项目管理系统

核心实体：
- User (用户)
- Team (团队)
- Sprint (冲刺)
- Story (故事)
- Task (任务)
```

#### 步骤 2：定义实体关系

```markdown
业务关系：
- Team 1:N User (团队成员)
- Team 1:N Sprint (冲刺)
- Sprint 1:N Story (故事)
- Story 1:N Task (任务)
- Task N:1 User (任务负责人)
```

### 5.2 实体定义阶段

#### 定义 ERD

```python
from pydantic_resolve import base_entity, Relationship, config_global_resolver

BaseEntity = base_entity()

class UserEntity(BaseModel, BaseEntity):
    """用户实体"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[TaskEntity], loader=user_to_tasks_loader),
        Relationship(field='id', target_kls=list[TeamEntity], loader=user_to_teams_loader),
    ]

    id: int
    name: str
    email: str

class TeamEntity(BaseModel, BaseEntity):
    """团队实体"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[SprintEntity], loader=team_to_sprints_loader),
        Relationship(field='id', target_kls=list[UserEntity], loader=team_to_users_loader),
    ]

    id: int
    name: str

class SprintEntity(BaseModel, BaseEntity):
    """冲刺实体"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[StoryEntity], loader=sprint_to_stories_loader),
    ]

    id: int
    name: str
    team_id: int

class StoryEntity(BaseModel, BaseEntity):
    """故事实体"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[TaskEntity], loader=story_to_tasks_loader),
    ]

    id: int
    name: str
    sprint_id: int

class TaskEntity(BaseModel, BaseEntity):
    """任务实体"""
    __relationships__ = [
        Relationship(field='owner_id', target_kls=UserEntity, loader=user_loader),
    ]

    id: int
    name: str
    owner_id: int
    story_id: int
    estimate: int

# 注册 ERD
diagram = BaseEntity.get_diagram()
config_global_resolver(diagram)
```

### 5.3 数据层实现

#### 定义 ORM Models（以 ERD 为指导）

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

class TeamMember(Base):
    """中间表：多对多关系"""
    __tablename__ = 'team_members'

    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role = Column(String(50))

class Sprint(Base):
    __tablename__ = 'sprints'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)

class Story(Base):
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    sprint_id = Column(Integer, ForeignKey('sprints.id', ondelete='CASCADE'), nullable=False)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    story_id = Column(Integer, ForeignKey('stories.id', ondelete='CASCADE'), nullable=False)
    estimate = Column(Integer, default=0)
```

#### 实现 Loaders

```python
from aiodataloader import DataLoader
from pydantic_resolve import build_list

async def user_loader(user_ids: list[int]):
    """加载用户"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = result.scalars().all()
        return build_list(users, user_ids, lambda u: u.id)

async def team_to_sprints_loader(team_ids: list[int]):
    """加载团队的 Sprint"""
    async with get_session() as session:
        result = await session.execute(
            select(Sprint).where(Sprint.team_id.in_(team_ids))
        )
        sprints = result.scalars().all()
        return build_list(sprints, team_ids, lambda s: s.team_id)

async def team_to_users_loader(team_ids: list[int]):
    """加载团队成员（通过中间表）"""
    async with get_session() as session:
        result = await session.execute(
            select(User)
            .join(TeamMember, TeamMember.user_id == User.id)
            .where(TeamMember.team_id.in_(team_ids))
        )
        users = result.scalars().all()

        # 构建映射：team_id -> list[User]
        users_by_team = {tid: [] for tid in team_ids}
        for user in users:
            for tm in user.team_memberships:
                if tm.team_id in users_by_team:
                    users_by_team[tm.team_id].append(user)

        return [users_by_team.get(tid, []) for tid in team_ids]

# 类似地实现其他 loaders...
```

### 5.4 API 实现阶段

#### 定义 Response Models

```python
from pydantic import BaseModel, Annotated
from pydantic_resolve import LoadBy, Resolver

class UserResponse(DefineSubset):
    __subset__ = (UserEntity, ('id', 'name'))

class TaskResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name', 'estimate'))

    owner: Annotated[Optional[UserResponse], LoadBy('owner_id')] = None

class StoryResponse(DefineSubset):
    __subset__ = (StoryEntity, ('id', 'name'))

    tasks: Annotated[list[TaskResponse], LoadBy('id')] = []

    # 计算总估算
    total_estimate: int = 0
    def post_total_estimate(self):
        return sum(t.estimate for t in self.tasks)

class SprintResponse(DefineSubset):
    __subset__ = (SprintEntity, ('id', 'name'))

    stories: Annotated[list[StoryResponse], LoadBy('id')] = []

class TeamResponse(DefineSubset):
    __subset__ = (TeamEntity, ('id', 'name'))

    sprints: Annotated[list[SprintResponse], LoadBy('id')] = []
    members: Annotated[list[UserResponse], LoadBy('id')] = []

    # 计算总任务数（需要跨层收集）
    total_tasks: int = 0
    def post_total_tasks(self):
        count = 0
        for sprint in self.sprints:
            for story in sprint.stories:
                count += len(story.tasks)
        return count
```

#### 实现 API Routes

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/teams", tags=['teams'])

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    session: AsyncSession = Depends(get_session)
):
    # 1. 从数据库获取基础数据
    team = await session.get(Team, team_id)
    await session.close()

    # 2. 转换为 Response Model
    team_response = TeamResponse.model_validate(team)

    # 3. 解析所有关联数据
    result = await Resolver().resolve(team_response)

    return result

@router.get("/", response_model=list[TeamResponse])
async def list_teams(session: AsyncSession = Depends(get_session)):
    # 1. 获取所有团队
    result = await session.execute(select(Team))
    teams = result.scalars().all()
    await session.close()

    # 2. 转换为 Response Models
    team_responses = [TeamResponse.model_validate(t) for t in teams]

    # 3. 批量解析
    result = await Resolver().resolve(team_responses)

    return result
```

### 5.5 可视化验证

#### 集成 FastAPI-Voyager

```python
from fastapi import FastAPI
from fastapi_voyager import create_voyager

app = FastAPI()

# 挂载 Voyager
app.mount('/voyager', create_voyager(
    app,
    er_diagram=diagram,  # 传入 ERD
    enable_pydantic_resolve_meta=True
))

# 注册路由
app.include_router(router)
```

#### 验证架构

1. **访问** `http://localhost:8000/voyager`
2. **检查 ERD**：确认实体关系正确显示
3. **点击 API**：查看数据流
4. **发现问题**：
   - 是否有循环依赖？
   - 是否有过度嵌套？
   - 是否有缺失的关系？

---

## 6. 与其他方案的对比

### 6.1 vs 传统 ORM

| 维度 | 传统 ORM (SQLAlchemy) | Pydantic-Resolve |
|------|----------------------|------------------|
| **关注点** | 数据持久化 | 业务数据组装 |
| **关系定义** | 基于外键约束 | 基于业务语义 |
| **数据加载** | Eager/Lazy Loading | DataLoader 批量加载 |
| **灵活性** | 受数据库结构限制 | 完全灵活 |
| **N+1 问题** | 容易出现，需手动优化 | 自动避免 |
| **业务表达** | 隐藏在查询中 | 显式声明 |
| **测试** | 依赖数据库 | 可独立测试 |

**代码对比**：

```python
# SQLAlchemy ORM
@router.get("/teams/{team_id}")
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Team)
        .options(
            selectinload(Team.sprints)
            .selectinload(Sprint.stories)
            .selectinload(Story.tasks)
        )
        .where(Team.id == team_id)
    )
    return result.scalar_one()

# Pydantic-Resolve
@router.get("/teams/{team_id}")
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    team = await session.get(Team, team_id)
    await session.close()
    return await Resolver().resolve(TeamResponse.model_validate(team))
```

### 6.2 vs GraphQL

| 维度 | GraphQL | Pydantic-Resolve |
|------|---------|------------------|
| **查询方式** | 前端自定义查询 | 后端定义 Schema |
| **类型安全** | 需要 SDL + 工具链 | 原生 Pydantic |
| **学习曲线** | 陡峭 | 平缓 |
| **性能** | DataLoader（手动配置） | DataLoader（自动） |
| **调试** | 复杂 | 简单（Python 代码） |
| **集成** | 需要额外服务器 | 原生 FastAPI |
| **灵活性** | 过于灵活，难以优化 | 明确的 API 契约 |
| **ERD 与用例分离** | 界限模糊，混合在 Schema 中 | 清晰分离，ERD 独立存在 |

**Schema 对比**：

```graphql
# GraphQL Schema - ERD 和用例混合
type Query {
    team(id: ID!): Team           # 用例
    teamMembers(id: ID!): [User]  # 另一个用例
}

type Team {
    id: ID!
    name: String!
    sprints: [Sprint!]!           # 实体关系
    members: [User!]!             # 实体关系
}

# 问题：Team 类型同时包含 ERD（实体定义）和多个用例的需求
# 难以区分：哪些是实体固有的关系？哪些是特定用例需要的数据？
```

```python
# Pydantic-Resolve - ERD 和用例清晰分离

# 1. ERD：业务实体关系（只定义一次）
class TeamEntity(BaseModel, BaseEntity):
    """业务实体 - 不关心用例"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[SprintEntity], loader=...),
        Relationship(field='id', target_kls=list[UserEntity], loader=...),
    ]
    id: int
    name: str

# 2. 用例 1：查看团队详情（包含 Sprint）
class TeamDetailResponse(DefineSubset):
    __subset__ = (TeamEntity, ('id', 'name'))
    sprints: Annotated[list[SprintResponse], LoadBy('id')] = []

@router.get("/teams/{team_id}", response_model=TeamDetailResponse)
async def get_team_detail(team_id: int): ...

# 3. 用例 2：查看团队成员（不包含 Sprint）
class TeamMembersResponse(DefineSubset):
    __subset__ = (TeamEntity, ('id', 'name'))
    members: Annotated[list[UserResponse], LoadBy('id')] = []

@router.get("/teams/{team_id}/members", response_model=TeamMembersResponse)
async def get_team_members(team_id: int): ...

# 优势：
# - ERD（TeamEntity）定义一次，多处复用
# - 不同用例有不同的 Response Model
# - 用例之间互不影响，易于维护
```

**关键差异**：

```
GraphQL 方式：
┌─────────────────────────────────┐
│      GraphQL Schema             │
│  ┌───────────────────────────┐  │
│  │   Type Team (混合)        │  │
│  │   - id, name (实体属性)   │  │
│  │   - sprints (用例 A 需要) │  │
│  │   - members (用例 B 需要)│  │
│  │   - tasks (用例 C 需要)  │  │
│  └───────────────────────────┘  │
│                                 │
│  问题：一个类型承载所有用例     │
│      难以组织，难以维护         │
└─────────────────────────────────┘

Pydantic-Resolve 方式：
┌─────────────────────────────────┐
│      ERD (核心实体)             │
│  ┌───────────────────────────┐  │
│  │   TeamEntity              │  │
│  │   - id, name              │  │
│  │   - 关系定义              │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
          ↓ 复用
┌─────────────────────────────────┐
│      用例层（API Route）        │
│  ┌──────────┐  ┌──────────┐    │
│  | 用例 A   |  | 用例 B   |    │
│  | TeamResp1|  | TeamResp2|    │
│  | (sprints)|  | (members)|    │
│  └──────────┘  └──────────┘    │
│                                 │
│  优势：每个用例独立，清晰       │
└─────────────────────────────────┘
```

**最佳实践的清晰性**：

| 问题 | GraphQL | Pydantic-Resolve |
|------|---------|------------------|
| 如何设计 Schema？ | 模糊：按实体？按用例？按字段？ | 清晰：ERD 定义实体，Response 定义用例 |
| 如何组织 Schema？ | 困难：所有东西在 Schema 中 | 简单：实体在 ERD，用例在 Route |
| 如何复用逻辑？ | 难以复用：Fragment 有限 | 易于复用：`DefineSubset` 继承实体 |
| 如何控制权限？ | 复杂：需要在 Resolver 层处理 | 清晰：不同 Route 有不同的权限控制 |

### 6.3 vs DDD 框架

| 维度 | DDD 框架 (如 Django-eav) | Pydantic-Resolve |
|------|------------------------|------------------|
| **复杂度** | 高（完整 DDD 实现） | 低（只关注数据组装） |
| **领域模型** | 强制使用 DDD 概念 | 灵活，可选择性使用 |
| **与 ORM 关系** | 封装 ORM | 与 ORM 协作 |
| **学习成本** | 高 | 低 |
| **适用场景** | 大型复杂领域 | 中小型项目 |

**架构对比**：

```
DDD 框架：
┌─────────────────────────┐
│  Application Layer      │
│  (Commands, Queries)    │
├─────────────────────────┤
│  Domain Layer           │
│  (Entities, Value objs) │
│  (Repositories)         │
│  (Domain Services)      │
├─────────────────────────┤
│  Infrastructure Layer   │
│  (ORM impl, DB)         │
└─────────────────────────┘

Pydantic-Resolve：
┌─────────────────────────┐
│  FastAPI Routes         │  (Use Cases)
├─────────────────────────┤
│  Response Models        │  (Interface)
│  (with resolve/post)    │
├─────────────────────────┤
│  Entity + ERD           │  (Domain)
├─────────────────────────┤
│  Loaders                │  (Repositories)
├─────────────────────────┤
│  SQLAlchemy ORM         │  (Infrastructure)
└─────────────────────────┘
```

---

## 7. 总结

### 核心价值

基于 Pydantic-Resolve 和 FastAPI-Voyager 的开发方法，实现了以下核心价值：

#### 1. 业务模型优先

```python
# ERD = 业务语言的直接表达
class TeamEntity(BaseModel, BaseEntity):
    """团队 - 业务概念"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[SprintEntity], loader=...),
    ]
```

- 业务关系显式声明
- 不受数据库结构限制
- 支持虚拟关系

#### 2. Clean Architecture 实现

```
依赖方向：
FastAPI Routes → Response Models → Entity + ERD → Loaders → ORM

符合 Clean Architecture 的依赖规则：
- 外层依赖内层
- 内层独立于外层
- 业务规则不依赖框架
```

#### 3. 自动性能优化

```python
# DataLoader 自动批量加载
tasks = [Task(1, owner_id=1), Task(2, owner_id=2), ...]
result = await Resolver().resolve(tasks)

# 自动合并为一次查询：
# SELECT * FROM users WHERE id IN (1, 2, ...)
```

- 避免 N+1 查询
- 自动批量加载
- 查询优化透明

#### 4. 架构可视化

```python
# FastAPI-Voyager 将架构可视化
app.mount('/voyager', create_voyager(
    app,
    er_diagram=diagram,
    enable_pydantic_resolve_meta=True
))
```

- 业务-技术映射图
- 实时更新
- 交互式探索

#### 5. 开发效率提升

| 阶段 | 传统方式 | 使用这套工具 |
|------|---------|-------------|
| 设计阶段 | 文字描述，容易遗漏 | ERD 可视化，清晰表达 |
| 开发阶段 | 手动组装数据，重复代码 | 声明式，自动解析 |
| 测试阶段 | 需要数据库 | 业务逻辑可独立测试 |
| 调试阶段 | 阅读代码，难以理解 | 图形化查看依赖关系 |
| 维护阶段 | 修改多处，容易出错 | 集中管理，影响分析 |

### 适用场景

#### 推荐使用

1. **复杂业务场景**
   - 多层嵌套关系
   - 跨实体数据聚合
   - 复杂的业务规则

2. **团队协作**
   - 需要清晰的架构文档
   - 新人频繁加入
   - 代码审查需求

3. **长期维护的项目**
   - 业务逻辑持续演进
   - 需要保持架构清晰
   - 防止技术债务积累

4. **性能敏感的应用**
   - 需要避免 N+1 查询
   - 需要批量加载优化
   - 需要灵活的查询策略

#### 不推荐使用

1. **简单的 CRUD 应用**
   - 单表操作
   - 无复杂关系
   - 可能过度设计

2. **实时性要求极高的场景**
   - DataLoader 的批量机制有轻微延迟
   - 对于超低延迟需求可能不合适

### 未来展望

这套方法还有很大的发展空间：

1. **工具链增强**
   - ERD → ORM Schema 生成器
   - ORM → ERD 反向生成
   - 自动化一致性检查

2. **性能优化**
   - 智能查询优化
   - 自动缓存策略
   - 查询计划分析

3. **生态集成**
   - 更多框架支持（Django, Litestar）
   - 监控和追踪集成
   - CI/CD 集成

### 结语

Pydantic-Resolve 和 FastAPI-Voyager 的组合，为 Python Web 开发提供了一种**以业务模型为核心**的架构方法。它不是要取代现有的工具（如 SQLAlchemy、FastAPI），而是**补充**它们在业务建模和数据组装方面的不足。

这套方法的核心思想是：

> **"让代码反映业务，而不是让业务适应代码"**

通过 ERD 显式声明业务关系，通过 Resolver 自动组装数据，通过 Voyager 可视化架构，我们能够构建更清晰、更可维护、更高性能的 Web 应用。

在软件架构的道路上，没有银弹。但这套方法至少为我们提供了一种**在实践中践行 Clean Architecture** 的可行路径。

---

## 参考资料

- [Pydantic-Resolve 文档](https://allmonday.github.io/pydantic-resolve/)
- [FastAPI-Voyager 仓库](https://github.com/allmonday/fastapi-voyager)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [DataLoader (Facebook)](https://github.com/facebook/dataloader)

---

**文档版本**: 1.0
**最后更新**: 2025-01-11
**作者**: tangkikodo
