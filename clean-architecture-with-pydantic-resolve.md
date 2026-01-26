# 基于 Pydantic-Resolve 和 FastAPI-Voyager 的 Clean Architecture 实践

> 一套面向复杂业务场景的 Python Web 开发方法论

## 目录

- [基于 Pydantic-Resolve 和 FastAPI-Voyager 的 Clean Architecture 实践](#基于-pydantic-resolve-和-fastapi-voyager-的-clean-architecture-实践)
  - [目录](#目录)
  - [1. 背景与问题](#1-背景与问题)
    - [1.1 当前主流做法及其痛点](#11-当前主流做法及其痛点)
      - [模式一：直接使用 ORM（如 SQLAlchemy）](#模式一直接使用-orm如-sqlalchemy)
      - [模式二：使用 ORM 的 Eager Loading](#模式二使用-orm-的-eager-loading)
      - [模式三：手动组装数据](#模式三手动组装数据)
      - [模式四：使用 GraphQL](#模式四使用-graphql)
    - [1.2 问题根源分析](#12-问题根源分析)
      - [问题 1：业务模型与数据模型混淆](#问题-1业务模型与数据模型混淆)
      - [问题 2：依赖方向错误](#问题-2依赖方向错误)
      - [问题 3：缺少业务关系的显式声明](#问题-3缺少业务关系的显式声明)
      - [问题 4：中间表的技术暴露](#问题-4中间表的技术暴露)
  - [2. Clean Architecture 思想](#2-clean-architecture-思想)
    - [2.1 核心原则](#21-核心原则)
      - [原则 1：依赖规则](#原则-1依赖规则)
      - [原则 2：业务规则独立](#原则-2业务规则独立)
      - [原则 3：跨边界的数据传递](#原则-3跨边界的数据传递)
    - [2.2 依赖规则](#22-依赖规则)
    - [2.3 在 Web 开发中的应用](#23-在-web-开发中的应用)
      - [传统架构的问题](#传统架构的问题)
  - [3. Pydantic-Resolve：业务模型层](#3-pydantic-resolve业务模型层)
    - [3.1 核心概念](#31-核心概念)
      - [核心思想](#核心思想)
    - [3.2 ERD：业务关系的声明](#32-erd业务关系的声明)
      - [定义实体关系图](#定义实体关系图)
      - [ERD 的关键特性](#erd-的关键特性)
    - [3.3 DataLoader：批量加载的秘密](#33-dataloader批量加载的秘密)
      - [问题：N+1 查询](#问题n1-查询)
      - [解决方案：DataLoader](#解决方案dataloader)
      - [DefineSubset：字段选择与复用](#definesubset字段选择与复用)
    - [3.4 Resolve 与 Post：数据组装与计算](#34-resolve-与-post数据组装与计算)
      - [Resolve：声明数据依赖](#resolve声明数据依赖)
      - [Post：数据后处理](#post数据后处理)
    - [3.5 跨层数据传递](#35-跨层数据传递)
      - [Expose：父节点向子节点暴露数据](#expose父节点向子节点暴露数据)
      - [Collect：子节点向父节点收集数据](#collect子节点向父节点收集数据)
    - [3.6 小结](#36-小结)
  - [4. FastAPI-Voyager：架构可视化](#4-fastapi-voyager架构可视化)
    - [4.0 为什么需要架构可视化？](#40-为什么需要架构可视化)
    - [4.1 核心功能](#41-核心功能)
      - [1. 自动扫描 API 结构](#1-自动扫描-api-结构)
      - [2. 三层架构展示](#2-三层架构展示)
    - [4.2 ERD 与 API Route 的结合](#42-erd-与-api-route-的结合)
      - [核心：业务-技术映射图](#核心业务-技术映射图)
    - [4.3 实战应用场景](#43-实战应用场景)
      - [场景 1：发现架构偏离](#场景-1发现架构偏离)
      - [场景 2：发现过度嵌套](#场景-2发现过度嵌套)
      - [场景 3：新人快速理解系统](#场景-3新人快速理解系统)
  - [5. 完整的开发流程](#5-完整的开发流程)
    - [5.1 架构设计阶段](#51-架构设计阶段)
      - [步骤 1：识别核心业务实体](#步骤-1识别核心业务实体)
      - [步骤 2：定义实体关系](#步骤-2定义实体关系)
    - [5.2 实体定义阶段](#52-实体定义阶段)
      - [定义 ERD](#定义-erd)
    - [5.3 数据层实现](#53-数据层实现)
      - [定义 ORM Models（以 ERD 为指导）](#定义-orm-models以-erd-为指导)
      - [实现 Loaders](#实现-loaders)
    - [5.4 API 实现阶段](#54-api-实现阶段)
      - [定义 Response Models](#定义-response-models)
      - [实现 API Routes](#实现-api-routes)
    - [5.5 可视化验证](#55-可视化验证)
      - [集成 FastAPI-Voyager](#集成-fastapi-voyager)
      - [验证架构](#验证架构)
  - [6. 与其他方案的对比](#6-与其他方案的对比)
    - [6.1 vs 传统 ORM](#61-vs-传统-orm)
    - [6.2 vs GraphQL](#62-vs-graphql)
    - [6.3 vs DDD 框架](#63-vs-ddd-框架)
  - [7. 总结](#7-总结)
    - [核心价值](#核心价值)
      - [1. 业务模型优先](#1-业务模型优先)
      - [2. Clean Architecture 实现](#2-clean-architecture-实现)
      - [3. 自动性能优化](#3-自动性能优化)
      - [4. 架构可视化](#4-架构可视化)
      - [5. 开发效率提升](#5-开发效率提升)
      - [6. 更易测试和调试](#6-更易测试和调试)
    - [适用场景](#适用场景)
      - [推荐使用](#推荐使用)
      - [不推荐使用](#不推荐使用)
    - [结语](#结语)
  - [参考资料](#参考资料)

---

## 前言

在 Python Web 开发中，处理复杂业务场景时，开发者往往面临一个两难选择：传统 ORM 方式简单直观但容易产生 N+1 查询问题，GraphQL 灵活强大但学习曲线陡峭且难以优化。更重要的是，业务模型与数据模型混淆、依赖方向错误等问题，导致代码难以维护，业务逻辑被技术实现细节绑架。

本文介绍一种基于 **Pydantic-Resolve** 和 **FastAPI-Voyager** 的 Clean Architecture 实践方法。这套方法的核心思想是：**让代码反映业务，而不是让业务适应代码**。通过 ERD（实体关系图）显式声明业务关系，实现业务模型与技术实现的解耦；通过 DataLoader 自动批量加载，透明地解决性能问题；通过 FastAPI-Voyager 可视化架构，让业务模型与用例的边界清晰可见。

文章将从问题根源分析入手，深入探讨 Clean Architecture 的依赖规则，详细讲解 Pydantic-Resolve 的核心概念（ERD、DataLoader、Resolve/Post、Expose/Collect 等），并展示完整的开发流程。无论你是正在寻找替代 GraphQL 的方案，还是希望改善现有项目的架构设计，相信都能从中获得启发。

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

这种做法在简单场景下确实很直观，能够快速上手。ORM 的类型安全特性也能在编译时发现一些错误，而且与数据库表结构的一一对应关系让代码容易理解。但当我们面对真正的业务场景时，这种方式的缺陷很快就暴露出来了。

最致命的问题是 N+1 查询。虽然代码看起来很清晰，但执行时会产生大量的数据库查询。每当我们访问一个关联关系时，ORM 就会发起一次新的查询。在深层嵌套的情况下，查询数量会呈指数级增长。更糟糕的是，这种性能问题在开发阶段不容易发现，只有当数据量积累到一定程度后才会显现出来，那时候往往已经太晚了。

代码的组织方式也是个问题。数据获取的逻辑散落在各个嵌套的循环中，业务逻辑和数据获取逻辑混在一起，难以阅读和维护。当需要修改业务规则时，开发者不得不在复杂的嵌套结构中寻找修改点，很容易引入新的 bug。性能更是不可控，随着数据量的增长，查询效率会急剧下降，而这些性能瓶颈很难在代码层面直接观察到。

此外，相似的数据获取逻辑会在多个 API 中重复出现，导致大量代码冗余。当一个 API 需要获取"团队及其 Sprint"，另一个 API 需要"团队及其成员"时，即使它们的查询逻辑非常相似，也不得不重复编写。这违反了 DRY（Don't Repeat Yourself）原则，增加了维护成本。

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

为了解决 N+1 查询问题，ORM 提供了 Eager Loading 机制，让我们可以通过 `joinedload`、`selectinload` 等方式预先加载关联数据。代码变得更简洁了，性能问题也得到了缓解。但这种方案也带来了新的挑战。

最明显的问题是笛卡尔积。当我们使用多层 JOIN 预加载关联数据时，数据库返回的数据量会急剧膨胀。比如一个团队有 10 个 Sprint，每个 Sprint 有 10 个 Story，每个 Story 有 10 个 Task，那么 JOIN 的结果集会包含 1000 行数据，即使每行的数据量不大，也会给网络传输和内存占用带来压力。

更严重的问题是灵活性差。Eager Loading 的策略是在代码中硬编码的，所有使用同一个 Model 的 API 都会执行相同的预加载逻辑。但不同的 API 往往需要不同的数据。比如一个 API 只需要团队的基本信息，另一个 API 需要团队的 Sprint，还有一个 API 需要团队的成员。如果统一使用 Eager Loading 加载所有关联数据，就会出现过度获取的问题，前端不需要的数据也被查询和传输了，浪费了资源。

配置 Eager Loading 本身就很复杂。开发者需要理解 `lazy`、`joinedload`、`selectinload`、`subquery` 等多种加载策略的区别，知道什么时候用哪一种，以及它们各自会有什么副作用。这种配置错误很容易导致性能问题或意外的数据加载行为。而且，这种"一刀切"的配置方式意味着所有 API 都使用相同的加载策略，无法针对特定场景进行优化。

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

为了获得最优的性能和精确的数据控制，有经验的开发者会选择手动组装数据。这种方式完全掌控查询逻辑，可以精确控制每个查询的 SQL 语句，避免不必要的数据库访问。通过批量查询和智能的数据组装，可以获得最佳的性能，而且没有冗余数据。

但这种方式的代价是代码变得非常冗长。如上面的例子所示，为了获取一个团队的完整信息，我们需要编写多个查询，手动构建数据字典，然后通过嵌套循环组装数据。代码的长度和复杂度都大幅增加，而真正表达业务逻辑的代码反而被淹没在数据组装的细节中。

更容易出错也是个大问题。手动组装数据涉及到大量的索引操作和循环嵌套，很容易出现索引错误、空指针引用等 bug。而且这些错误往往只有在运行时、特定数据条件下才会暴露，难以在开发阶段发现。

维护成本更是高昂。当业务规则发生变化时（比如需要添加一个新的关联关系），开发者需要在所有相关的 API 中修改数据组装逻辑。如果遗漏了某个地方，就会导致数据不一致。而且，相似的数据组装逻辑会在多个 API 中重复出现，违反了 DRY 原则。

最根本的问题是，这种代码已经变成了纯粹的数据搬运工，看不出任何业务意图。代码中充满了字典操作、循环嵌套、索引查找，而这些都是技术细节，与业务需求毫无关系。新加入的团队成员很难从这些代码中理解业务逻辑，业务知识的传递变得异常困难。

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

GraphQL 确实是一个很有吸引力的方案。前端可以按需获取数据，需要什么字段就查什么字段，不会有过度获取的问题。它提供了类型安全的查询接口，而且通过 DataLoader 可以自动解决 N+1 查询问题。这些特性让 GraphQL 在前端开发中广受欢迎。

但 GraphQL 的学习曲线非常陡峭。开发者需要学习全新的查询语言、Schema 定义、Resolver 编写、DataLoader 配置等一堆概念，这与 REST API 的直观性形成了鲜明对比。更麻烦的是，GraphQL 的过度灵活性给后端带来了巨大的挑战。前端可以构造任意复杂的查询，有些查询甚至可能是开发者没有想到过的，这导致后端很难进行针对性的优化。当一个查询嵌套了 10 层，返回了数百万条数据时，数据库和服务器都会面临巨大的压力。

调试 GraphQL API 也比调试 REST API 复杂得多。当一个 GraphQL 查询出错时，错误信息往往很难定位到具体的问题源头。而且 GraphQL 需要额外的服务器和工具链支持，无法直接利用现有的 FastAPI 生态系统。比如 FastAPI 的依赖注入、中间件、自动文档生成等特性，在 GraphQL 中都无法直接使用。

还有一个更深层次的问题是 ERD 和用例的界限模糊。GraphQL 的 Schema 同时扮演了实体模型和查询接口两个角色。当我们设计一个 GraphQL Schema 时，很难确定应该按照实体来组织（一个 Type 对应一个数据库表），还是按照用例来组织（不同的业务场景需要不同的字段）。这导致最佳实践不清晰，不同的项目、不同的开发者可能有完全不同的组织方式。

而且随着业务增长，所有的用例都会堆砌在同一个 Schema 中，导致 Schema 膨胀，难以维护。权限控制也变得异常复杂。不同的 API 端点可能有不同的权限要求，但它们可能都查询同一个实体（比如 User），在 GraphQL 中很难针对不同的查询场景应用不同的权限规则。

### 1.2 问题根源分析

上面我们探讨的所有模式，虽然表面上的问题各不相同，但它们的核心困境其实是一致的。

#### 问题 1：业务模型与数据模型混淆

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

在传统的 ORM 开发中，业务模型和数据模型是混在一起的。看看这个例子，`Team` 类既表达了业务概念（团队是什么），又承载了数据模型的细节（如何在数据库中存储）。当我们在 `sprints` 字段上定义 `relationship` 时，这到底是在描述一个业务关系（团队有多个 Sprint），还是在声明一个数据库外键约束？这种模糊性会导致很多问题。

数据库的设计约束会直接影响我们的业务建模。比如，如果数据库中的 `teams` 表没有直接到 `users` 的外键，而是通过中间表 `team_members` 关联，那么在 ORM 中我们也必须通过这个中间表来定义关系。这意味着业务模型被迫适应数据库的实现细节，而不是反过来。

更严重的是，这种方式无法表达跨库、跨服务的业务关系。现代系统中，数据可能分布在不同的数据库中，甚至存储在外部服务里。比如用户的基本信息在 PostgreSQL，而用户的偏好设置在 MongoDB，用户的实时状态在 Redis 中。ORM 的 `relationship` 无法跨越这些边界，业务模型因此被限制在了单一数据库的范围内。

#### 问题 2：依赖方向错误

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

这违反了 Clean Architecture 的依赖规则。正确的依赖关系应该是：业务规则最稳定，不依赖任何外层；数据库是实现细节，应该依赖业务规则；当数据库变化时，业务规则不应该受影响。但传统架构的依赖方向恰恰相反，业务规则被数据库的实现细节所绑架。

#### 问题 3：缺少业务关系的显式声明

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

业务关系没有被显式声明出来，这是个很隐蔽但危害很大的问题。看看这个例子，"团队的任务"是一个清晰的业务概念，但这个概念被隐藏在 SQL 的 JOIN 和 WHERE 子句中。新加入团队的成员需要阅读大量代码才能理解系统中有哪些业务关系，这些关系是如何定义的。更糟糕的是，没有自动化的方式来检查业务关系的一致性。当需求变化需要修改某个关系时，开发者很难找到所有相关的代码，很容易遗漏某个地方，导致业务逻辑的不一致。

#### 问题 4：中间表的技术暴露

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

这个问题的根源在于，ORM 的多对多关系需要显式定义中间表，这导致技术细节直接泄漏到业务层代码中。业务代码必须知道 `team_members` 中间表的存在，查询时也需要显式地 join 这个中间表。这增加了代码复杂度，更重要的是，业务逻辑被数据库的实现细节所绑架。

更深层的问题是业务语义变得模糊。`TeamMember` 到底是一个有意义的业务概念，还是纯粹的技术实现？如果中间表还有额外的字段（比如 `role` 表示用户在团队中的角色，`joined_at` 表示加入时间），这些字段应该被建模为独立的实体吗？不同的开发者可能给出不同的答案，缺乏统一的指导原则。

数据组装也因此变得复杂。查询"团队的所有成员"需要 join 中间表，查询"用户所属的团队"也需要 join 中间表。所有涉及多对多关系的查询都变得冗长和难以理解。当业务规则要求"获取用户在所有团队中的角色"时，情况就更加复杂了。这些技术细节让业务逻辑的实现变得异常沉重。

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

| 维度           | SQLAlchemy ORM         | Pydantic-Resolve ERD      |
| -------------- | ---------------------- | ------------------------- |
| **中间表位置** | 暴露在业务层           | 隐藏在 loader 实现中      |
| **业务语义**   | 技术关系 (`secondary`) | 业务关系 (`团队包含成员`) |
| **查询代码**   | 需要 join 中间表       | `loader.load(team_id)`    |
| **代码位置**   | 分散在多处             | 集中在 loader             |
| **测试**       | 依赖数据库表结构       | 可 mock loader            |

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

遵循依赖规则有几个关键点需要注意。首先，内层不知道外层的存在，这意味着核心业务逻辑不依赖于任何框架、数据库或 UI 的细节。其次，内层不包含外层的信息，比如业务规则不应该知道数据是用 PostgreSQL 还是 MongoDB 存储的。最后，外层的实现可以随时替换而不影响内层，这意味着我们可以从 SQLAlchemy 切换到 MongoDB，或者从 FastAPI 切换到 Django，而业务逻辑代码无需修改。

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
┌────────────────────────────────────────────────────┐
│         Presentation Layer (外层)                   │
│  - FastAPI Routes                                   │
│  - Request/Response Models                          │
│  - 依赖: Application Layer                          │
└────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│      Application Layer (Use Cases)                 │
│  - 业务用例（获取用户、创建订单）                    │
│  - 依赖: Domain Layer                               │
└────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│           Domain Layer (内层)                      │
│  - Entities (业务实体)                              │
│  - Business Rules (业务规则)                        │
│  - Value Objects (值对象)                           │
│  - 不依赖任何外层                                    │
└────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│    Infrastructure Layer (最外层)                   │
│  - Database (SQLAlchemy)                           │
│  - External Services                               │
│  - File System                                     │
└────────────────────────────────────────────────────┘
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

这段代码暴露了传统架构的核心问题。SQLAlchemy 虽然建立了对象关系映射（ORM），让数据库表可以通过 Python 对象来操作，但这种映射关系过于紧密。ORM Model 既承担了数据持久化的职责，又要表达业务概念，导致对象无法自由地代表业务模型。业务实体被数据库的实现细节所绑架，每个字段、每个关系都必须与数据库表结构一一对应，完全失去了作为独立业务概念存在的自由。

更深层次的问题包括：

1. **Domain Layer 被 SQLAlchemy 绑定**：业务实体继承了 SQLAlchemy 的 Base，无法独立于数据库存在
2. **业务逻辑无法脱离数据库测试**：编写单元测试时必须启动完整的数据库环境，大大降低了测试效率
3. **切换数据库需要修改所有层**：当从 PostgreSQL 迁移到 MongoDB 时，所有使用 ORM Model 的代码都需要重写

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

这两种方式的本质差异在于关注点不同。命令式方法关注"如何获取"（how），需要开发者手动编写数据获取的逻辑，容易产生 N+1 查询问题。而声明式方法关注"想要什么"（what），通过描述数据结构来声明依赖关系，具体的数据获取逻辑由框架自动处理，既简化了代码又避免了性能陷阱。

### 3.2 ERD：业务关系的声明

#### 定义实体关系图

```python
from pydantic_resolve import base_entity, Relationship, MultipleRelationship, Link, config_global_resolver

# 1. 创建 BaseEntity
BaseEntity = base_entity()

# 2. 定义业务实体
class UserEntity(BaseModel, BaseEntity):
    """用户实体 - 业务概念"""
    __relationships__ = [
        # 同一个字段 'id' 到同一目标类型的多个业务关系
        MultipleRelationship(
            field='id',
            target_kls=list[TaskEntity],
            links=[
                Link(biz='created', loader=user_to_created_tasks_loader),
                Link(biz='assigned', loader=user_to_assigned_tasks_loader),
            ]
        ),
        # 用户所属的团队
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

这种定义方式体现了 ERD 的核心优势。从 entity 和 relationship 的定义出发，relationship 相关的数据并不需要提前在 entity 里面定义好 field name。Entity 只需要定义业务概念的核心属性（如 id、name），而关联关系通过 `__relationships__` 单独声明。这种定义方式更加接近存储模型，将数据结构的定义与数据的获取方式完全解耦。

更重要的是，这种设计为后续通过继承、扩展来组合 response 数据结构提供了良好的基础。当需要为不同的 API 返回不同的数据时，只需继承 Entity 并选择需要的关系，而不需要在 Entity 中预定义所有可能的字段。这种灵活性让同一个 Entity 可以适应各种不同的业务场景，真正实现了"一次定义，多处复用"。

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

这个功能在传统的 SQLAlchemy ORM 中是很难实现的。在 ORM 中，如果 User 和 Task 之间存在多种关联关系（创建、分配、审核），通常只能通过定义多个 `relationship` 属性来实现，但这些属性都必须在 Model 类中预先定义，而且无法清晰地区分它们的业务语义。更糟糕的是，ORM 的关系定义受到数据库外键约束的限制，如果没有对应的数据库表结构，这些关系就无法表达。

但 MultipleRelationship 就不同了。它通过 `biz` 参数为每个关系赋予了清晰的业务含义，这些业务含义直接反映在代码中，让关系本身成为了业务知识的载体。`created`、`assigned`、`reviewed` 不仅仅是技术标识，更是业务领域的直接表达。这种设计更符合真实的业务现状，因为一个用户与任务之间的关系确实可以有多种业务含义，而 ERD 让这些业务关系得以显式声明和清晰区分。

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

这种设计带来了显著的优势。首先是数据源无关性，关系定义完全不关心数据从哪里来，无论是数据库、文件系统、RPC 服务、消息队列还是外部 API，业务逻辑都保持一致。这意味着一个实体的关联数据可以来自多个不同的数据源，比如 UserEntity 的 tasks 来自数据库，config 来自本地文件，profile 来自 RPC 服务，所有这些异构数据源在业务层看起来没有任何区别。

其次是技术解耦。当需要更换数据源时，只需修改 loader 的实现，ERD 定义和业务逻辑无需任何改动。比如可以从本地配置文件平滑迁移到配置中心（etcd/Consul），而业务层代码完全感知不到变化。最后是性能优化的灵活性，可以根据业务需求为不同数据选择最合适的存储：热点数据放 Redis，大文件计算结果放对象存储，实时状态从消息队列订阅，真正实现"术业有专攻"。

**与传统 ORM 的对比**：

| 维度           | 传统 ORM (SQLAlchemy)   | Pydantic-Resolve ERD      |
| -------------- | ----------------------- | ------------------------- |
| **数据源**     | 仅限数据库              | 任何数据源                |
| **关系定义**   | `relationship()` + 外键 | `Relationship()` + loader |
| **跨服务查询** | 需要手动调用 API        | 无缝集成，就像本地查询    |
| **混合数据源** | 困难                    | 天然支持                  |
| **测试**       | 需要数据库              | 可 mock loader            |

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

DataLoader 的工作原理基于智能的批量和缓存机制。当多个 load 请求在同一个事件循环中发起时，它们不会立即执行，而是先被缓存起来等待。例如连续调用 load(1)、load(2)、load(3)，这些请求会被暂存。如果再次调用 load(1)，由于缓存命中会立即返回之前的结果。当事件循环到达合适的时机，所有缓存的唯一 ID 会被合并成一次批量调用 batch_load_fn([1, 2, 3])，查询结果再分配给各个等待的请求。

这种机制带来了三个关键特性。首先是自动批量，单个请求被自动合并成批量请求，无需开发者手动编写批量逻辑。其次是智能缓存，同一个 ID 在一次解析周期内只会查询一次，重复请求直接返回缓存结果。最后是并发调度，利用 Python 的事件循环机制自动协调批量时机，开发者无需关心底层的调度细节。

#### DefineSubset：字段选择与复用

在实际开发中，不同的 API 往往需要返回同一实体的不同字段组合。比如一个 API 只需要用户的基本信息（id、name），另一个 API 需要用户的详细信息（id、name、email），还有一个 API 需要用户的统计数据。如果为每个 API 都定义一个完整的 Response Model，会产生大量重复代码。`DefineSubset` 提供了一种优雅的方式来复用 Entity 定义，只选择需要的字段。

**基本用法**

```python
from pydantic_resolve import DefineSubset

# Entity 定义了完整的业务实体
class UserEntity(BaseModel, BaseEntity):
    __relationships__ = [...]
    id: int
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime

# 通过 DefineSubset 选择需要的字段
class UserSummary(DefineSubset):
    __subset__ = (UserEntity, ('id', 'name', 'email'))

# 自动生成等价的：
# class UserSummary(BaseModel):
#     id: int
#     name: str
#     email: str
```

这种方式带来的好处是显而易见的：首先，字段类型自动从 Entity 继承，无需重复定义；其次，当 Entity 字段变更时，所有基于它的 Response Model 都会自动反映这种变更；最后，代码更加简洁，减少了大量重复劳动。

**高级配置：SubsetConfig**

如果需要更复杂的配置（比如同时暴露字段给子节点，或者发送到收集器），可以使用 `SubsetConfig`：

```python
from pydantic_resolve import DefineSubset, SubsetConfig

class StoryResponse(DefineSubset):
    __subset__ = SubsetConfig(
        kls=StoryEntity,                       # 源模型
        fields=['id', 'name', 'owner_id'],     # 要包含的字段
        expose_as=[('name', 'story_name')]     # 暴露给子节点的别名
    )

# 等价于：
# class StoryResponse(BaseModel):
#     id: int
#     name: Annotated[str, ExposeAs('story_name')]
#     owner_id: int
```

**与 ERD 的协同**

`DefineSubset` 与 ERD 配合使用时，效果更佳。Entity 通过 ERD 定义了所有可能的关系，而 Response Model 通过 `DefineSubset` 选择当前需要的字段和关系。这种分离让业务定义和使用场景完全解耦。

```python
# Entity 定义：业务实体的完整模型
class TaskEntity(BaseModel, BaseEntity):
    __relationships__ = [
        Relationship(field='owner_id', target_kls=UserEntity, loader=user_loader),
        Relationship(field='story_id', target_kls=StoryEntity, loader=story_loader),
    ]
    id: int
    name: str
    estimate: int
    owner_id: int
    story_id: int

# API 1：只需要任务基本信息
class TaskSummaryResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name'))

# API 2：需要任务及其负责人
class TaskWithOwnerResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name', 'estimate', 'owner_id'))
    owner: Annotated[Optional[UserResponse], LoadBy('owner_id')] = None

# API 3：需要任务及其所属的 Story
class TaskWithStoryResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name', 'story_id'))
    story: Annotated[Optional[StoryResponse], LoadBy('story_id')] = None
```

**核心理念**

`DefineSubset` 体现了"定义一次，多处复用"的设计哲学。Entity 是业务概念的完整定义，是"真相的唯一来源"；Response Model 是针对特定用例的字段选择，是"使用场景的适配器"。这种分离确保了业务定义的一致性，同时又保留了足够的灵活性来适应各种不同的 API 需求。

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

Resolver 的工作流程分为四个步骤。首先扫描 Response Model 中所有的 `resolve_{field}` 方法，识别出需要解析的字段。然后收集所有需要加载的 ID，比如有 100 个 Task 对象，可能会产生 50 个不同的 owner_id。接着批量调用对应的 loader，一次查询获取所有需要的 User 数据。最后将查询结果按照 ID 映射关系填充到对应的字段中，整个过程完全自动化。

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

执行顺序经过精心设计以确保数据依赖的正确性。首先执行所有 resolve 方法，这些方法可以并行执行，因为它们之间没有依赖关系。然后等待所有异步操作完成，确保所有关联数据都已加载完毕。最后执行所有 post 方法，这些方法串行执行，因为它们可能需要访问 resolve 方法加载的数据，或者进行跨字段的数据计算。这种两阶段设计保证了在计算派生字段时，所有基础数据都已经准备就绪。

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

### 3.6 小结

Pydantic-Resolve 通过多个维度的抽象，将构建业务数据中常见的模式进行了适当粒度的抽象，形成了一个简洁而强大的工具集。

**核心抽象维度**：

1. **ERD（实体关系图）**：将业务关系的定义与数据获取完全解耦，通过声明式的方式描述实体之间的关系
2. **DataLoader**：自动批量加载，避免 N+1 查询问题，将性能优化透明化
3. **DefineSubset**：从 Entity 选择字段组合，实现"定义一次，多处复用"，避免重复代码
4. **Resolve/Post**：分离数据加载与数据计算，让每个方法职责单一
5. **Expose/Collect**：提供跨层数据传递能力，支持父节点向子节点暴露数据和子节点向父节点收集数据
6. **LoadBy**：基于 ERD 自动解析关系，减少重复代码

这些抽象维度之间保持正交，每个维度解决一个特定的问题，互不干扰又可以自由组合。DefineSubset 负责字段选择，ERD 负责定义关系，LoadBy 负责使用关系，DataLoader 负责批量加载，Resolve/Post 负责数据组装与计算，Expose/Collect 负责跨层数据传递。

各司其职。

---

## 4. FastAPI-Voyager：架构可视化

### 4.0 为什么需要架构可视化？

如果你使用过 GraphQL，一定对 GraphiQL 印象深刻。GraphiQL 是一个交互式的 IDE，让你可以：

- 浏览完整的 GraphQL Schema
- 探索每个 Type 的字段和关系
- 实时编写和测试查询
- 查看查询结果的类型信息

GraphiQL 的核心价值在于：**它让不可见的 Schema 变得可见和可探索**。开发者不再需要阅读大量文档或代码，就能快速理解 GraphQL API 的结构。

但在 RESTful API + Pydantic-Resolve 的架构中，我们面临类似的挑战。虽然我们有 ERD 定义业务实体关系，有 Response Model 定义 API 返回结构，但这些信息散落在代码的各个地方。如果没有工具支持，开发者需要：

- 阅读大量代码才能理解业务关系
- 手动追踪数据流向
- 难以发现架构偏离或过度嵌套

**FastAPI-Voyager 就像是 Pydantic-Resolve 世界的 GraphiQL**。

它提供了类似的交互式探索体验，但面向的是 RESTful API 架构：

- **可视化 ERD**：看到所有实体及其关系
- **API 依赖图**：查看每个 API 返回的数据结构及其依赖
- **交互式探索**：点击任意节点查看上下游依赖
- **实时更新**：代码变更后自动刷新视图

但更重要的是，Voyager 提供了 GraphiQL 所没有的独特优势：

| 维度         | GraphiQL (GraphQL)      | FastAPI-Voyager (Pydantic-Resolve) |
| ------------ | ----------------------- | ---------------------------------- |
| **业务模型** | Schema 混合了实体和用例 | ERD 独立定义业务实体               |
| **用例边界** | 模糊，难以区分          | 清晰，每个 Route 是一个用例        |
| **关系定义** | 隐藏在 Schema 中        | 显式声明在 ERD 中                  |
| **数据流**   | 需要阅读 Resolver       | 可视化展示依赖链路                 |
| **性能洞察** | 难以发现 N+1            | 颜色标记 resolve/post 操作         |

GraphiQL 让 GraphQL 的 Schema 变得可见，而 Voyager 让业务模型和用例的分离变得可见。它不仅展示了 API 的结构，更重要的是展示了**业务模型如何被不同的用例所使用**，这正是 Clean Architecture 的核心思想。

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

**在线演示**：体验 [FastAPI-Voyager Live Demo](https://www.newsyeah.fun/voyager/?tag=demo)，查看真实项目的架构可视化效果。

#### 2. 三层架构展示

```
┌────────────────────────────────────┐
│  Tag Layer (用例分组)               │
│  ┌────────┐  ┌────────┐  ┌────────┐│
│  | users  |  | teams  |  | tasks  ││
│  └────┬───┘  └────┬───┘  └────┬───┘│
└───────┼────────────┼────────────┼───┘
        │            │            │
        ↓            ↓            ↓
┌────────────────────────────────────┐
│  Route Layer (接口层)               │
│  ┌────────────┐  ┌────────────┐   │
│  | GET /users |  | POST /teams|   │
│  └──────┬─────┘  └──────┬─────┘   │
└─────────┼────────────────┼─────────┘
          │                │
          ↓                ↓
┌────────────────────────────────────┐
│  Schema Layer (业务模型层)          │
│  ┌──────┐  ┌──────┐  ┌──────┐    │
│  | User |←─| Team |→─| Task |    │
│  └──────┘  └──────┘  └──────┘    │
└────────────────────────────────────┘
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

pydantic-resolve 的操作通过颜色编码来直观展示。绿色标记的 resolve 字段表示通过 DataLoader 加载的数据，这些字段的数据来自外部数据源。蓝色标记的 post 字段表示在所有数据加载完成后计算得出的派生字段。紫色标记的 expose as 字段表示父节点向后代节点暴露的数据，用于跨层访问。红色标记的 send to 字段表示数据会发送到父节点的收集器。黑色标记的 collectors 字段则表示从所有子节点收集上来的聚合数据。这种颜色编码让数据流向一目了然，开发者可以快速理解每个字段的数据来源和用途。

### 4.3 实战应用场景

#### 场景 1：发现架构偏离

在实际开发中，API 实现很容易偏离最初设计的业务模型。比如 ERD 中只定义了 User 到 Task 的关系，但某个 API 的 Response Model 却包含了 Profile 字段。这种偏离在传统代码审查中很难发现，但在 Voyager 中却一目了然。只需点击 `get_user` route，就能看到它返回的 `UserWithProfileResponse` 结构。如果 ERD 图中没有 `User → Profile` 的链接，立刻就能识别出这个 API 实现偏离了业务模型，需要补充 ERD 定义或者修改 Response Model。

#### 场景 2：发现过度嵌套

过度嵌套是影响 API 性能和可维护性的常见问题。当一个 API 返回 Team → Sprints → Stories → Tasks → Owner 这样五层嵌套的数据时，查询复杂度会急剧上升。在 Voyager 中，这个问题很容易发现。只需点击 `get_team` route，就能看到一条长长的依赖链，链路的长度直观地反映了嵌套深度。如果发现某个 API 的嵌套层级过深，就应该考虑将其拆分为多个 API，或者使用字段选择机制让前端按需获取数据。

#### 场景 3：新人快速理解系统

新团队成员快速上手一直是个挑战。传统方式下，新人需要阅读几百页的文档，查看散落在各处的代码，还需要不断询问老员工才能理解系统架构。使用 Voyager 后，这个过程被大大简化。新人只需打开 /voyager 页面，点击感兴趣的 API，就能立即看到该 API 依赖的模型和关系。通过交互式探索，新人可以在五分钟内理解核心业务流程，而无需阅读大量文档或代码。这种可视化的学习方式大大降低了团队知识传递的成本。

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

集成完成后，通过可视化来验证架构设计的正确性。首先访问 `http://localhost:8000/voyager` 查看整个系统的架构视图。检查 ERD 部分确认实体关系是否正确显示，所有预期的业务关系都应该清晰地展示出来。然后点击各个 API 查看具体的数据流，每个 API 返回的 Response Model 及其依赖关系应该一目了然。在这个过程中重点检查几个常见问题：是否存在循环依赖导致的数据加载困难，是否有过度嵌套影响性能，是否有缺失的业务关系导致某些字段无法自动解析。通过这种可视化的验证方式，可以在开发早期就发现架构问题，而不是等到上线后才发现。

---

## 6. 与其他方案的对比

### 6.1 vs 传统 ORM

| 维度         | 传统 ORM (SQLAlchemy) | Pydantic-Resolve    |
| ------------ | --------------------- | ------------------- |
| **关注点**   | 数据持久化            | 业务数据组装        |
| **关系定义** | 基于外键约束          | 基于业务语义        |
| **数据加载** | Eager/Lazy Loading    | DataLoader 批量加载 |
| **灵活性**   | 受数据库结构限制      | 完全灵活            |
| **N+1 问题** | 容易出现，需手动优化  | 自动避免            |
| **业务表达** | 隐藏在查询中          | 显式声明            |
| **测试**     | 依赖数据库            | 可独立测试          |

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

| 维度               | GraphQL                    | Pydantic-Resolve       |
| ------------------ | -------------------------- | ---------------------- |
| **查询方式**       | 前端自定义查询             | 后端定义 Schema        |
| **类型安全**       | 需要 SDL + 工具链          | 原生 Pydantic          |
| **学习曲线**       | 陡峭                       | 平缓                   |
| **性能**           | DataLoader（手动配置）     | DataLoader（自动）     |
| **调试**           | 复杂                       | 简单（Python 代码）    |
| **集成**           | 需要额外服务器             | 原生 FastAPI           |
| **灵活性**         | 过于灵活，难以优化         | 明确的 API 契约        |
| **ERD 与用例分离** | 界限模糊，混合在 Schema 中 | 清晰分离，ERD 独立存在 |

**Schema 对比**：

```graphql
# GraphQL Schema - ERD 和用例混合
type Query {
  team(id: ID!): Team # 用例
  teamMembers(id: ID!): [User] # 另一个用例
}

type Team {
  id: ID!
  name: String!
  sprints: [Sprint!]! # 实体关系
  members: [User!]! # 实体关系
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
┌───────────────────────────────┐
│      GraphQL Schema           │
│  ┌─────────────────────────┐  │
│  │   Type Team (混合)      │  │
│  │   - id, name (实体属性) │  │
│  │   - sprints (用例 A)    │  │
│  │   - members (用例 B)    │  │
│  │   - tasks (用例 C)      │  │
│  └─────────────────────────┘  │
│                               │
│  问题：一个类型承载所有用例    │
│      难以组织，难以维护        │
└───────────────────────────────┘

Pydantic-Resolve 方式：
┌───────────────────────────────┐
│      ERD (核心实体)           │
│  ┌─────────────────────────┐  │
│  │   TeamEntity            │  │
│  │   - id, name            │  │
│  │   - 关系定义            │  │
│  └─────────────────────────┘  │
└───────────────────────────────┘
          ↓ 复用
┌───────────────────────────────┐
│    用例层（API Route）        │
│  ┌──────────┐  ┌──────────┐  │
│  | 用例 A   |  | 用例 B   |  │
│  |TeamResp1 |  |TeamResp2 |  │
│  |(sprints) |  |(members) |  │
│  └──────────┘  └──────────┘  │
│                               │
│  优势：每个用例独立，清晰      │
└───────────────────────────────┘
```

**最佳实践的清晰性**：

| 问题              | GraphQL                        | Pydantic-Resolve                      |
| ----------------- | ------------------------------ | ------------------------------------- |
| 如何设计 Schema？ | 模糊：按实体？按用例？按字段？ | 清晰：ERD 定义实体，Response 定义用例 |
| 如何组织 Schema？ | 困难：所有东西在 Schema 中     | 简单：实体在 ERD，用例在 Route        |
| 如何复用逻辑？    | 难以复用：Fragment 有限        | 易于复用：`DefineSubset` 继承实体     |
| 如何控制权限？    | 复杂：需要在 Resolver 层处理   | 清晰：不同 Route 有不同的权限控制     |

### 6.3 vs DDD 框架

| 维度            | DDD 框架 (如 Django-eav) | Pydantic-Resolve     |
| --------------- | ------------------------ | -------------------- |
| **复杂度**      | 高（完整 DDD 实现）      | 低（只关注数据组装） |
| **领域模型**    | 强制使用 DDD 概念        | 灵活，可选择性使用   |
| **与 ORM 关系** | 封装 ORM                 | 与 ORM 协作          |
| **学习成本**    | 高                       | 低                   |
| **适用场景**    | 大型复杂领域             | 中小型项目           |

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

这种方法让业务关系得到显式声明，所有实体关系都在 ERD 中清晰定义，不再隐藏在代码或 SQL 语句中。更重要的是，业务建模完全不受数据库结构限制，可以表达跨库、跨服务的业务关系，甚至支持从 RPC、文件系统等非数据库源加载数据的虚拟关系。真正实现了业务概念与技术实现的解耦。

#### 2. Clean Architecture 实现

```
依赖方向从外层到内层清晰明确：FastAPI Routes → Response Models → Entity + ERD → Loaders → ORM。这完全符合 Clean Architecture 的依赖规则。外层依赖内层，内层完全独立于外层，业务规则不依赖任何框架或技术实现。当需要更换数据库、ORM 框架或 Web 框架时，核心业务逻辑无需任何修改。
```

#### 3. 自动性能优化

```python
# DataLoader 自动批量加载
tasks = [Task(1, owner_id=1), Task(2, owner_id=2), ...]
result = await Resolver().resolve(tasks)

# 自动合并为一次查询：
# SELECT * FROM users WHERE id IN (1, 2, ...)
```

DataLoader 的自动批量加载机制让性能优化变得透明。开发者无需担心 N+1 查询问题，所有关联数据的加载都会被自动合并成批量查询。查询优化是透明的，开发者只需声明数据依赖，框架会自动选择最优的查询策略。这种"默认高性能"的设计让开发者可以专注于业务逻辑，而不用担心性能陷阱。

#### 4. 架构可视化

```python
# FastAPI-Voyager 将架构可视化
app.mount('/voyager', create_voyager(
    app,
    er_diagram=diagram,
    enable_pydantic_resolve_meta=True
))
```

FastAPI-Voyager 将架构以可视化的方式呈现出来，提供了业务模型与技术实现的映射图。开发者可以直观地看到每个 API 返回的数据结构、依赖关系和数据流向。视图会随着代码变更实时更新，始终保持与代码同步。更重要的是提供了交互式探索能力，点击任意节点就能查看其依赖关系和被依赖关系，让架构理解变得前所未有的简单。

#### 5. 开发效率提升

| 阶段     | 传统方式               | 使用这套工具         |
| -------- | ---------------------- | -------------------- |
| 设计阶段 | 文字描述，容易遗漏     | ERD 可视化，清晰表达 |
| 开发阶段 | 手动组装数据，重复代码 | 声明式，自动解析     |
| 测试阶段 | 需要数据库             | 业务逻辑可独立测试   |
| 调试阶段 | 阅读代码，难以理解     | 图形化查看依赖关系   |
| 维护阶段 | 修改多处，容易出错     | 集中管理，影响分析   |

#### 6. 更易测试和调试

```python
# DataLoader：功能单一，易于测试
async def user_loader(user_ids: list[int]):
    """批量加载用户 - 只做一件事，把 ID 映射到用户"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = result.scalars().all()
        return build_list(users, user_ids, lambda u: u.id)

# 测试非常简单：mock loader 即可
async def test_task_response():
    # 不需要数据库
    mock_users = [User(id=1, name="Alice")]
    with patch('user_loader', return_value=mock_users):
        result = await Resolver().resolve(tasks)
        assert result[0].owner.name == "Alice"
```

DataLoader 的查询逻辑相比普通做法中的嵌套 SQL 要简单得多。每个 loader 只负责一个简单的批量查询：根据 ID 列表返回对应的数据。这种功能单一的设计让 loader 非常容易测试，只需要 mock 输入和输出，无需启动完整的数据库环境。

更重要的是，在调试时也容易隔离问题。当某个 API 的数据加载出现问题时，可以通过 Voyager 快速定位到是哪个 loader 出错，然后单独测试这个 loader。这种"小而专注"的函数设计让调试变得前所未有的简单。相比传统方式中那些几百行的复杂 SQL 或者嵌套的数据组装逻辑，单个 loader 的代码量通常只有十几行，问题排查和修复都更加高效。

### 适用场景

#### 推荐使用

这套方法最适合复杂业务场景，当系统中存在多层嵌套关系、需要跨实体数据聚合、或者有复杂的业务规则时，它的优势会非常明显。对于团队协作场景，特别是需要清晰的架构文档、新人频繁加入、或者有严格代码审查需求的团队，可视化的架构图能够显著提升沟通效率。长期维护的项目也能从中受益，业务逻辑持续演进的过程中，ERD 帮助保持架构清晰，防止技术债务积累。对于性能敏感的应用，需要避免 N+1 查询、需要批量加载优化、或者需要灵活查询策略的场景，DataLoader 的自动批量机制能够带来显著的性能提升。

#### 不推荐使用

当然，这套方法并不适合所有场景。对于简单的 CRUD 应用，如果只有单表操作、没有复杂的关联关系，使用这套方法可能会过度设计，反而增加了不必要的复杂度。对于实时性要求极高的场景，DataLoader 的批量机制会带来轻微的延迟（虽然通常在毫秒级别），对于某些超低延迟需求（如高频交易）可能不太合适。在这种情况下，直接使用手写的优化查询可能会有更好的性能表现。

### 结语

Pydantic-Resolve 和 FastAPI-Voyager 的组合，为 Python Web 开发提供了一种**以业务模型为核心**的架构方法。它不是要取代现有的工具（如 SQLAlchemy、FastAPI），而是**补充**它们在业务建模和数据组装方面的不足。

这套方法的核心思想是：

> **"让代码反映业务，而不是让业务适应代码"**

更深层地说，这套做法的核心思想是**尊重业务复杂度**，在此基础上尽量压缩相关的代码复杂度。业务本身是复杂的，有各种实体关系、业务规则、用例场景，这些复杂度是无法避免的。但代码的复杂度可以通过抽象和封装来降低。

Pydantic-Resolve 通过类似 DSL 的方式，将常见的代码模式封装到若干个清晰的概念中：

- **ERD** 封装了业务关系的声明
- **DataLoader** 封装了批量加载的逻辑
- **Resolve/Post** 封装了数据组装和计算的流程
- **Expose/Collect** 封装了跨层数据传递的模式
- **LoadBy** 封装了关系的复用逻辑

这些概念就像是特定于数据组装领域的 DSL（Domain Specific Language），让开发者可以用声明式的方式描述"想要什么"，而不是用命令式的方式编写"如何获取"。原本散落在各处的代码噪音——批量查询的循环、字典映射的构建、嵌套数据的组装、缓存的管理——都被封装到这些概念之中，从而大大降低了整体的代码复杂度。

当阅读使用 Pydantic-Resolve 编写的代码时，开发者看到的不再是充满技术细节的数据搬运逻辑，而是清晰的业务意图。这种降噪效果让代码更易于理解、更易于维护、更易于演进。

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
