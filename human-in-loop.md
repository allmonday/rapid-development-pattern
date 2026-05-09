## 声明式数据组装的四段论开发方法论

### 背景

传统开发模式中，数据模型、数据获取、API 组装、前端消费混杂在一起，层间纠缠严重。迭代时一个改动牵动全局，AI 生成代码更是缺乏约束、不可验证。

本方法论基于 **pydantic-resolve**（声明式数据组装）+ **fastapi-voyager**（可视化），将后端开发拆分为四个职责单一的阶段，每层单向依赖，变更隔离。同时与大模型结合，AI 逐层生成代码，每层由人审查产出后再进入下一层，确保过程稳定可控。

---

### Phase 1：定义业务语义

**产出：Pydantic Schema + ER Diagram + Mock Query/Mutation**

这一层只回答一个问题：**系统里有哪些实体，它们之间什么关系，能做什么操作？**

```python
# 实体定义
BaseEntity = base_entity()

class UserEntity(BaseModel, BaseEntity):
    id: int
    name: str

class TaskEntity(BaseModel, BaseEntity):
    __relationships__ = [
        Relationship(fk='owner_id', name='owner', target=UserEntity, loader=user_loader),
        Relationship(fk='sprint_id', name='sprint', target=SprintEntity, loader=sprint_loader),
    ]
    id: int
    title: str
    owner_id: int
    sprint_id: int

# Mock Query/Mutation —— 接口先行，实现后补
async def query_tasks(filters: TaskFilter) -> list[TaskEntity]:
    return MOCK_TASKS

async def mutate_create_task(input: CreateTaskInput) -> TaskEntity:
    return MOCK_NEW_TASK
```

**关键特征：**
- 纯业务语义，不依赖任何 ORM、数据库或外部服务
- ER Diagram 即设计文档，可用 fastapi-voyager 直接可视化，团队在写代码前就能看到系统全貌
- Mock 接口让前后端可以并行开发
- AI 生成后，人审查实体和关系是否正确

**这一层做完，系统的骨架就定了。**

---

### Phase 2：实现数据获取层

**产出：每个 Relationship 对应的 Loader 实现 + 测试覆盖**

这一层回答：**每个关系背后的数据从哪来？**

```python
# 来自数据库（ORM）
async def user_loader(user_ids: list[int]):
    users = await db.query(User).filter(User.id.in_(user_ids)).all()
    return build_object(users, user_ids, lambda u: u.id)

# 来自微服务 Batch RPC
async def org_loader(org_ids: list[int]):
    resp = await httpx.post("http://org-service/batch", json={"ids": org_ids})
    return build_object(resp.json(), org_ids, lambda o: o["id"])

# 来自缓存
async def config_loader(config_ids: list[str]):
    values = await redis.mget(config_ids)
    return build_object(values, config_ids, lambda c: c.id)
```

**关键特征：**
- **数据源无关** —— 这是核心架构优势。Relationship 描述的是"实体之间的关系"，不是"数据存在哪里"。同一个 ER Diagram 中的关系可以横跨数据库、RPC、Redis、Elasticsearch 等任意数据源
- 微服务架构下，一个响应结构可能涉及三四个服务，但组装层完全无感知
- ORM 只是其中一种手段，不是唯一手段
- 这一层的 Loader 是纯函数，测试简单直接，mock 也统一（替换 loader 即可）
- AI 生成后，人审查每个 loader 的正确性和性能（批处理对齐、max_batch_size 等）

**这一层做完，所有数据通道就通了。**

---

### Phase 3：按 Use Case 组装 API

**产出：具体的 API 端点，每个端点是一个明确的业务场景**

这一层回答：**每个接口应该返回什么结构？**

```python
# Sprint 看板 —— 需要 tasks、owner、统计数据
class TaskCardView(TaskEntity):
    owner: Annotated[Optional[UserEntity], AutoLoad(), SendTo('contributors')] = None

class SprintBoardResponse(SprintEntity):
    tasks: Annotated[list[TaskCardView], AutoLoad()] = []
    task_count: int = 0
    contributors: list[UserView] = []

    def post_task_count(self):
        return len(self.tasks)

    def post_contributors(self, collector=Collector('contributors')):
        return collector.values()

@app.get("/sprints/{id}/board", tags=["sprint-board"])
async def get_sprint_board(id: int):
    sprint = await query_sprint(id)
    return await Resolver().resolve([SprintBoardResponse.model_validate(sprint)])

# Sprint 报告 —— 同样的 SprintEntity，不同的组装方式
class SprintReportResponse(SprintEntity):
    tasks: Annotated[list[TaskEntity], AutoLoad()] = []
    velocity: int = 0
    # ... 不同的派生字段
```

**关键特征：**
- 不同接口复用同一个 Entity 和 Relationship，只是组装方式不同
- Use Case 驱动，不是 CRUD 驱动 —— 每个 API 都是一个具体业务场景
- OpenAPI tag 在此阶段按页面/功能域规划好，为 Phase 4 做准备
- AI 生成后，人审查响应结构是否符合业务需求

**这一层做完，后端 API 全部就绪，OpenAPI spec 自动生成。**

---

### Phase 4：生成前端 SDK 与 UI

**产出：TS SDK + 页面级 API 分类 + 前端 UI**

这一层回答：**前端怎么消费这些 API？**

```
FastAPI OpenAPI spec
    ↓ 自动生成
TS SDK（按 tag 分类为页面级模块）
    ↓
前端页面调用
```

**关键特征：**
- OpenAPI spec 是 Phase 3 的自动产物，零额外成本
- tag 分类让每个页面对应一组 API，前端开发边界清晰
- fastapi-voyager 可可视化"哪些页面用了哪些 API"，帮助前端理解依赖
- 前端框架可替换（React/Vue/Svelte），完全不影响后端三层

**这一层做完，完整的交付闭环形成。**

---

### 层间关系总结

```
Phase 1 (Schema/ERD/Mock)     ← 业务语义，人的审查重点
    ↓ Entity 类型 + Relationship 定义
Phase 2 (Loader 实现 + 测试)   ← 数据获取，人的审查重点
    ↓ query/mutation 函数签名
Phase 3 (API 组装)             ← 业务场景，人的审查重点
    ↓ OpenAPI spec（按 tag 分类）
Phase 4 (TS SDK + 前端)        ← 前端消费
```

**单向依赖，变更隔离：**

| 变更场景 | 影响范围 |
|----------|----------|
| 加一个字段 | Phase 1 → 2 → 3 → 4（逐层传播） |
| 改 API 响应结构 | 只改 Phase 3 |
| 换数据库 | 只改 Phase 2 |
| 换前端框架 | 只改 Phase 4 |
| 加一个新接口 | Phase 3 加 Response 类，Phase 4 重新生成 |

---

### 与 AI 结合的关键

传统方式让 AI 一次生成整个系统，缺乏约束，不可验证，容易失控。

四段论将生成过程拆为**四个可独立验证的阶段**：

1. AI 生成 Phase 1 → 人审查实体和关系 → fastapi-voyager 可视化确认
2. AI 生成 Phase 2 → 人审查 loader 实现 → 跑测试确认
3. AI 生成 Phase 3 → 人审查 API 响应结构 → 跑接口测试确认
4. AI 生成 Phase 4 → 人审查前端页面

**每一层的输入是上一层的结构化产出，不是模糊的自然语言描述。** 这让 AI 的生成空间被严格约束，产出可预测、可验证、可回滚。

> 本质上，四段论解决的不是"怎么写代码"的问题，而是"怎么让 AI 写代码的过程变得像工程一样可控"的问题。