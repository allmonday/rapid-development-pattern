# 四阶段开发流程

> 基于 pydantic-resolve + FastAPI 的分层开发模式

本文档从当前项目中提取出四阶段开发流程。每个阶段有明确的产物和边界，后续阶段依赖前序阶段的产物但不修改它们。

```
Phase 1                Phase 2                Phase 3               Phase 4
Schema + ERD  ──────>  ORM + Tests  ──────>  RESTful APIs  ──────>  TS SDK + UI
(建模阶段)              (实现阶段)              (接口阶段)             (集成阶段)
```

---

## Phase 1：Schema + ER Diagram + Mock Data

**目标**：定义业务实体、实体间关系，以及用于开发测试的种子数据。此阶段不涉及数据库和 ORM。

### 1.1 定义 Entity Schema

每个 service 目录下创建 `schema.py`，定义继承 `BaseModel + BaseEntity` 的实体类。

以 Sprint 为例（`src/services/sprint/schema.py`）：

```python
from pydantic import BaseModel, ConfigDict
from pydantic_resolve import query, mutation
from typing import Optional
import src.services.story.schema as story_schema
from src.services.er_diagram import BaseEntity
from src.db import async_session
from .query import get_sprints as get_sprints_query
from . import mutation as sprint_mutation

class Sprint(BaseModel, BaseEntity):
    __relationships__ = []

    id: int
    name: str
    status: str
    team_id: int

    @query
    async def get_sprints(cls) -> list['Sprint']:
        async with async_session() as session:
            sprints = await get_sprints_query(session)
            return [Sprint.model_validate(sprint) for sprint in sprints]

    @mutation
    async def update_sprint(cls, id: int, name: Optional[str] = None,
                            status: Optional[str] = None) -> Optional['Sprint']:
        async with async_session() as session:
            sprint = await sprint_mutation.update_sprint(session, id, name, status)
            return Sprint.model_validate(sprint) if sprint else None

    @mutation
    async def create_story(cls, sprint_id: int, name: str,
                           owner_id: int) -> story_schema.Story:
        async with async_session() as session:
            story = await sprint_mutation.create_story(session, sprint_id, name, owner_id)
            return story_schema.Story.model_validate(story)

    model_config = ConfigDict(from_attributes=True)
```

**要点**：
- `@query` 装饰器声明查询入口，GraphQL 和 MCP 可直接消费
- `@mutation` 装饰器声明写操作，包括自身 CRUD 和子实体管理
- `__relationships__ = []` 留空，关系由 Phase 2 的 ORM 集成自动填充

Team 的 schema 展示了聚合根管理子实体的模式（`src/services/team/schema.py`）：

```python
class Team(BaseModel, BaseEntity):
    __relationships__ = []

    id: int
    name: str

    @query
    async def get_teams(cls) -> list['Team']: ...

    # 自身 CRUD
    @mutation
    async def create_team(cls, name: str) -> 'Team': ...
    @mutation
    async def delete_team(cls, id: int) -> bool: ...

    # 管理 Sprint 子实体
    @mutation
    async def create_sprint(cls, team_id: int, name: str,
                            status: str = 'planning') -> sprint_schema.Sprint: ...
    @mutation
    async def delete_sprint(cls, id: int) -> bool: ...

    # 管理团队成员 (M2M)
    @mutation
    async def add_team_member(cls, team_id: int, user_id: int) -> bool: ...
    @mutation
    async def remove_team_member(cls, team_id: int, user_id: int) -> bool: ...
```

### 1.2 ER Diagram 基座

在 `src/services/er_diagram.py` 中创建全局 ER Diagram 基座：

```python
from pydantic_resolve import base_entity

BaseEntity = base_entity()
diagram = None
AutoLoad = None
```

所有 Entity Schema 继承 `BaseEntity` 后自动注册到 diagram。Phase 2 中 `initialize()` 会将 ORM 关系合并进来。

### 1.3 Mock Data

每个 service 目录下创建 `mock.py`，提供开发/测试用的种子数据（`src/services/sprint/mock.py`）：

```python
from .model import Sprint

_sprints = [
    dict(id=1, name="Sprint A W1", status="close", team_id=1),
    dict(id=2, name="Sprint A W3", status="active", team_id=1),
    dict(id=3, name="Sprint A W5", status="plan", team_id=1),
    dict(id=4, name="Sprint B W1", status="close", team_id=2),
    dict(id=5, name="Sprint B W3", status="active", team_id=2),
    dict(id=6, name="Sprint B W5", status="plan", team_id=2),
]

sprints = [Sprint(**s) for s in _sprints]
```

### Phase 1 产物清单

每个 service 目录下：
- `schema.py` — Entity 定义 + `@query` / `@mutation`
- `mock.py` — 种子数据
- `src/services/er_diagram.py` — BaseEntity + initialize() 入口

---

## Phase 2：ORM + Relationships + Query/Mutation + Tests

**目标**：实现具体的数据库模型、查询/变更逻辑，并完成 service 层的测试覆盖。Phase 1 的 schema 不做修改。

### 2.1 ORM Model

每个 service 创建 `model.py`，定义 SQLAlchemy ORM 模型。关系用 `relationship(lazy="noload")` 声明但不自动加载（`src/services/sprint/model.py`）：

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
import src.db as db

class Sprint(db.Base):
    __tablename__ = "sprint"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(String(100))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))

    stories: Mapped[list["Story"]] = relationship(lazy="noload", order_by="Story.id")
```

多对多关系通过关联表实现（`src/services/team/model.py`）：

```python
class TeamUser(db.Base):
    __tablename__ = "team_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))

class Team(db.Base):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    sprints: Mapped[list["Sprint"]] = relationship(lazy="noload", order_by="Sprint.id")
    users: Mapped[list["User"]] = relationship(
        secondary=TeamUser.__table__, lazy="noload", order_by="User.id")
```

### 2.2 ORM → ER Diagram 集成

在 `er_diagram.py` 的 `initialize()` 中，将 ORM 关系映射到 Entity Schema（`src/services/er_diagram.py`）：

```python
def initialize():
    global diagram, AutoLoad

    from pydantic_resolve.integration.sqlalchemy import build_relationship
    from pydantic_resolve.integration.mapping import Mapping
    import src.db as db
    import src.services.user.model as user_orm
    # ... 其他 ORM 和 DTO 导入

    diagram = BaseEntity.get_diagram()

    orm_entities = build_relationship(
        mappings=[
            Mapping(entity=user_dto.User, orm=user_orm.User),
            Mapping(entity=team_dto.Team, orm=team_orm.Team),
            Mapping(entity=sprint_dto.Sprint, orm=sprint_orm.Sprint),
            Mapping(entity=story_dto.Story, orm=story_orm.Story),
            Mapping(entity=task_dto.Task, orm=task_orm.Task),
        ],
        session_factory=db.async_session,
    )

    diagram = diagram.add_relationship(orm_entities)
    AutoLoad = diagram.create_auto_load()
```

`build_relationship` 读取 ORM 的 `relationship()` 定义，自动生成对应的 DataLoader 并注册到 diagram。之后 `AutoLoad` 即可在 Phase 3 的 router schema 中使用。

### 2.3 Query & Mutation 实现

`query.py` 提供具体的数据库查询函数（`src/services/sprint/query.py`）：

```python
from .model import Sprint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_sprints(session: AsyncSession):
    return (await session.execute(select(Sprint))).scalars().all()

async def get_sprints_by_ids(ids: list[int], session: AsyncSession):
    return (await session.execute(
        select(Sprint).where(Sprint.id.in_(ids))
    )).scalars().all()
```

`mutation.py` 提供具体的变更函数（`src/services/sprint/mutation.py`）：

```python
async def update_sprint(session: AsyncSession, id: int,
                        name: Optional[str] = None,
                        status: Optional[str] = None) -> Optional[Sprint]:
    result = await session.execute(select(Sprint).where(Sprint.id == id))
    sprint = result.scalar_one_or_none()
    if sprint:
        if name is not None: sprint.name = name
        if status is not None: sprint.status = status
        await session.commit()
        await session.refresh(sprint)
    return sprint

async def create_story(session: AsyncSession, sprint_id: int,
                       name: str, owner_id: int) -> Story:
    story = Story(sprint_id=sprint_id, name=name, owner_id=owner_id)
    session.add(story)
    await session.commit()
    await session.refresh(story)
    return story
```

### 2.4 Service 级别测试

测试只覆盖 service 层（query + loader），router 层不需要测试（`src/services/sprint/tests/`）：

```python
# test_query.py
async def test_sprint_by_id2(session):
    result = await sq.get_sprints_by_ids([1], session)
    assert len(result) == 1
    assert result[0].name == 'Sprint A W1'
```

```python
# test_loader.py
async def test_loader(session_factory, monkeypatch):
    monkeypatch.setattr(src.db, 'async_session', session_factory)
    loader = DataLoader(batch_load_fn=ld.team_to_sprint_loader)
    result = await loader.load(1)
    assert len(result) == 3
```

**原则**：数据源可靠 + 组合过程可靠 = 视图数据可靠。service 测试覆盖前者，pydantic-resolve 保证后者。

### Phase 2 产物清单

每个 service 目录下新增：
- `model.py` — SQLAlchemy ORM 模型 + relationship
- `query.py` — 异步查询函数
- `mutation.py` — 异步变更函数
- `loader.py` — DataLoader（部分由 ORM 集成自动生成）
- `tests/` — query 和 loader 的测试

全局更新：
- `src/services/er_diagram.py` — `initialize()` 中添加 Mapping

---

## Phase 3：RESTful APIs by Use Case

**目标**：根据具体业务场景（use case），组合 service 层的 schema 来构建 API 响应。Phase 3 只新增 router，不修改 service。

### 3.1 View Schema 组合

每个 router 目录下创建 `schema.py`，通过继承 + `AutoLoad()` 声明数据组合方式（`src/router/sample_1/schema.py`）：

```python
from typing import Optional, Annotated
from pydantic_resolve import serialization
from src.services.er_diagram import AutoLoad

import src.services.story.schema as ss
import src.services.task.schema as ts
import src.services.user.schema as us
import src.services.sprint.schema as sps
import src.services.team.schema as tms

@serialization
class Sample1TaskDetail(ts.Task):
    user: Annotated[Optional[us.User], AutoLoad(origin='owner')] = None

@serialization
class Sample1StoryDetail(ss.Story):
    tasks: Annotated[list[Sample1TaskDetail], AutoLoad()] = []
    owner: Annotated[Optional[us.User], AutoLoad()] = None

@serialization
class Sample1SprintDetail(sps.Sprint):
    stories: Annotated[list[Sample1StoryDetail], AutoLoad()] = []

@serialization
class Sample1TeamDetail(tms.Team):
    sprints: Annotated[list[Sample1SprintDetail], AutoLoad()] = []
    members: Annotated[list[us.User], AutoLoad(origin='users')] = []
```

**要点**：
- 继承 service schema 获得字段
- `AutoLoad()` 利用 Phase 2 建立的 ER Diagram 关系自动加载数据
- `@serialization` 标记为序列化视图（不注册到 ER Diagram）
- 每个 router 的 schema 是独立的 use case，互不影响

### 3.2 Router 定义

`router.py` 遵循统一的三步模式：query → validate → resolve（`src/router/sample_1/router.py`）：

```python
from fastapi import APIRouter
from pydantic_resolve import Resolver
import src.db as db

route = APIRouter(tags=['sample_1'], prefix="/sample_1")

@route.get('/teams-with-detail', response_model=List[Sample1TeamDetail])
async def get_teams_with_detail(session: AsyncSession = Depends(db.get_session)):
    # 1. 从 service query 获取根数据
    teams = await tmq.get_teams(session)
    # 2. 转为 view schema
    teams = [Sample1TeamDetail.model_validate(t) for t in teams]
    # 3. Resolver 自动解析所有 AutoLoad 字段
    teams = await Resolver().resolve(teams)
    return teams
```

### 3.3 Tag 组织

每个 router 用 `tags` 参数标记 API 分组：

```python
route = APIRouter(tags=['sample_1'], prefix="/sample_1")  # Sample 1
route = APIRouter(tags=['sample_2'], prefix="/sample_2")  # Sample 2
# ...
```

Tag 在 Phase 4 中决定了生成的 TS SDK 类名和前端页面分组。

### 3.4 应用初始化顺序

`main.py` 中的导入顺序保证正确的初始化链：

```python
# 1. 导入 BaseEntity
from src.services.er_diagram import BaseEntity

# 2. 导入所有 Entity Schema（触发注册）
import src.services.user.schema
import src.services.team.schema
# ...

# 3. 构建 Diagram + ORM 集成
from src.services import er_diagram
er_diagram.initialize()

# 4. 配置全局 Resolver
from pydantic_resolve import config_global_resolver
config_global_resolver(diagram)

# 5. 导入 Router（使用 AutoLoad）
import src.router.sample_1.router as s1_router
# ...

# 6. 注册 Router
app.include_router(s1_router.route)
```

### Phase 3 产物清单

每个 router 目录下：
- `schema.py` — View schema（继承 service schema + AutoLoad）
- `router.py` — FastAPI routes with tags

全局更新：
- `src/main.py` — import router + `app.include_router()`

---

## Phase 4：TS SDK + Frontend UI

**目标**：从 OpenAPI schema 自动生成 TypeScript SDK，按 tag 分组构建前端页面。

### 4.1 SDK 生成配置

`fe-demo/openapi-ts.config.ts`：

```typescript
export default defineConfig({
  input: 'http://localhost:8001/openapi.json',
  output: {
    fileName: { suffix: '.gen' },
    path: 'src/sdk',
    header: ['// @ts-nocheck'],
  },
  plugins: [
    '@hey-api/client-fetch',
    '@hey-api/typescript',
    { name: '@hey-api/sdk', asClass: true },
  ],
});
```

运行 `npm run generate-client` 即可生成 SDK。

### 4.2 生成的 SDK 结构

FastAPI 的 tag 直接映射为 SDK class：

```typescript
// sdk.gen.ts
export class Sample1 {
    public static getTasksWithDetail(...)  // GET /sample_1/tasks-with-detail
    public static getStoriesWithDetail(...)  // GET /sample_1/stories-with-detail
    public static getSprintsWithDetail(...)
    public static getTeamsWithDetail(...)
}

export class Sample2 {
    public static getTeamsWithDetailOfMultipleLevel(...)
}
// ... Sample3 ~ Sample7
```

类型定义也按 response_model 自动生成：

```typescript
// types.gen.ts
export interface Sample1TeamDetail {
    id: number;
    name: string;
    sprints: Sample1SprintDetail[];
    members: User[];
}
```

### 4.3 前端页面使用 SDK

```vue
<script setup lang="ts">
import { Sample1, Sample1TeamDetail } from 'src/sdk';
import { onMounted, ref } from 'vue';

const teams = ref<Sample1TeamDetail[]>([]);

onMounted(async () => {
  teams.value = (await Sample1.getTeamsWithDetail()).data!;
});
</script>
```

**完整链路**：

```
Service Schema ──继承──> Router View Schema ──OpenAPI──> TS Types
                                     │                        │
Service Query ──> Router Handler ──> JSON Response ──> SDK Class Method
```

### Phase 4 产物清单

- `fe-demo/src/sdk/` — 生成的 TypeScript SDK（不需要手动维护）
- `fe-demo/src/pages/` — 前端页面组件

---

## 总结：文件结构映射

```
src/services/<name>/          # Phase 1 + Phase 2
├── schema.py                 # [Phase 1] Entity Schema + @query + @mutation
├── mock.py                   # [Phase 1] 种子数据
├── model.py                  # [Phase 2] SQLAlchemy ORM + relationship
├── query.py                  # [Phase 2] 查询函数
├── mutation.py               # [Phase 2] 变更函数
├── loader.py                 # [Phase 2] DataLoader（部分自动生成）
└── tests/                    # [Phase 2] 测试
    ├── conftest.py
    ├── test_query.py
    └── test_loader.py

src/services/er_diagram.py    # [Phase 1+2] BaseEntity + initialize()

src/router/<name>/            # Phase 3
├── schema.py                 # View Schema (AutoLoad 组合)
└── router.py                 # FastAPI routes (tags)

src/main.py                   # Phase 3 (初始化 + 注册)

fe-demo/                      # Phase 4
├── openapi-ts.config.ts      # SDK 生成配置
└── src/
    ├── sdk/                  # 生成的 TS SDK
    └── pages/                # 前端页面
```

**阶段间的依赖关系**：

```
Phase 1 (schema, mock, er_diagram base)
    │
    ▼
Phase 2 (orm, query, mutation, loader, tests, er_diagram initialize)
    │
    ▼
Phase 3 (router schema with AutoLoad, router.py, main.py)
    │
    ▼
Phase 4 (openapi-ts config, generated SDK, frontend pages)
```

每个阶段只依赖前序阶段的产物，不反向修改。这使得：
- Schema 建模（Phase 1）可以先行，不阻塞讨论
- ORM 实现（Phase 2）可以独立开发和测试
- API 组合（Phase 3）灵活应对需求变化，不影响 service 层
- 前端集成（Phase 4）完全自动化，零手写 HTTP 代码
