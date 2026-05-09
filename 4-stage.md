# 四段论开发方法论 — 权限 Plugin 设计总结

> 基于 pydantic-resolve + AI 的分层开发模式，本文聚焦 Phase 3 权限 Plugin 的设计。

---

## 一、四段论框架回顾

| Phase | 职责 | 产出 |
|-------|------|------|
| **Phase 1** | Pydantic Schema + ER Diagram + 聚合根入口操作 | 业务实体定义，纯语义，不依赖数据源 |
| **Phase 2** | Loader 实现 + 测试 | 数据获取，数据源无关（ORM/HTTP RPC/Redis/ES） |
| **Phase 3** | 按 Use Case 组装 API 响应 + 权限 Plugin | API 响应结构 + 访问控制 |
| **Phase 4** | OpenAPI spec → TS SDK → 前端 UI | 端到端 SDK |

**核心原则：层间单向依赖，变更隔离。**

---

## 二、权限 Plugin 的设计哲学

### 2.1 类比中间表

```
多对多关系：
  User ── user_roles ──► Role
  User 不知道自己有哪些 Role
  Role 不知道自己被哪些 User 持有
  关系信息完全在中间表里

权限也是一样：
  User ── 权限规则 ──► Entity
  User 不知道自己对什么有权限
  Entity 不知道自己被什么权限规则保护
  关系信息完全在权限层（Plugin）
```

**Entity 保持纯粹的业务数据，不感知权限的存在。**

### 2.2 前提条件：ER Diagram

Permission Plugin 依赖 ER Diagram + AutoLoad 模式，这是设计前提：

```
ER Diagram 知道关系结构 (dept → project → document)
    ↓
scope_desc 不需要手写，从 Relationship 链自动推导
    ↓
权限系统返回的 scope 树和 ER Diagram 的关系结构天然对齐
    ↓
AutoLoad 已经知道如何沿关系加载数据，自然也知道如何用 scope 约束加载
```

不使用 ER Diagram 的项目（纯 Core API 模式）不在本 Plugin 的适用范围内。

### 2.3 为什么是 Plugin 而不是框架核心

| 场景 | 效果 |
|------|------|
| 不需要权限的项目 | 不加载 Plugin，零负担 |
| 需要权限的项目 | 在 Phase 3 加载 Plugin，AutoLoad 自动约束 |
| 更换权限策略 | 换 Plugin，Phase 1/2 不动 |
| 测试 | Entity 和 Loader 的测试完全不需要 mock 权限 |

### 2.4 Plugin 的归属

```
Phase 1: Entity + ER Diagram   纯业务，不知道权限存在           ✅
Phase 2: Loader                接受更少的 keys，不感知原因       ✅ 不感知权限规则
Phase 3: AutoLoad + Plugin     AutoLoad 读 scope 约束 Loader    ✅ 唯一知道 scope 的地方
                               Plugin 计算 scope 树 + 注册 hook 传播 scope
Phase 4: SDK / 前端            不知道后端怎么鉴权               ✅
```

---

## 三、核心机制：Scope 预计算 + 树状约束

### 3.1 总体流程

```
请求进入
  │
  │  user_id + action + ER Diagram（关系结构的唯一来源）
  │
  ▼
① 从 ER Diagram 的 Relationship 链自动推导层级描述，查询权限系统
   输入：user_id, action, 自动推导的层级描述
   输出：树状的可达 scope（ID 列表 / filter 闭包 / 无约束）
   │
   ▼
② scope 挂到根对象（类似 pagination_tree 的 attach）
   │
   ▼
③ AutoLoad 读取 scope 自动约束 Loader
   resolved_hooks 将子 scope 传播到 resolved children
   │
   ▼
④ Loader 收到约束（ID 集合或 filter 闭包），不感知权限
```

### 3.2 Step 1：权限系统查询

**输入**——层级描述从 ER Diagram 自动生成，不需要手写：

```python
# ER Diagram 定义了关系：DeptEntity → ProjectEntity → DocumentEntity
# Plugin 从 Relationship 链自动推导出：
scope_desc = {
    "department": {
        "project": {
            "document": {}
        }
    }
}

# 查询权限系统
scope_tree = await permission_plugin.compute_scope(
    user_id=123,
    action="read",
    scope_desc=scope_desc,  # 自动生成，非人工维护
)
```

**输出**——scope 树支持三种形态（详见第六节）：

```json
{
  "department": [
    {
      "id": 1,
      "project": [{"id": 1}, {"id": 2}]
    },
    {
      "id": 3,
      "project": [
        {"id": 5, "document": [{"id": 7}]}
      ]
    }
  ]
}
```

关键特征：
- **层级描述自动生成**：从 ER Diagram 的 Relationship 链推导，与业务关系定义同源
- **树状输出**：保留层级关系，不是扁平 ID 列表
- **稀疏覆盖**：dept{1} 下 project{2} 没有 document 子节点，意味着该分支无约束，AutoLoad 正常加载
- **只返回权限已知的部分**：不主动展开业务数据，避免"鸡生蛋"问题

**RBAC 和 ABAC 共用嵌套结构**，区别在于子节点的约束深度：

```json
// RBAC scope 树：子节点没有更深的约束节点
{
  "department": [
    {"id": 1, "project": [{"id": 1}, {"id": 2}]},
    {"id": 3, "project": [{"id": 5}]}
  ]
  // project{1} 的子节点 document 没有 document 子树 → 无约束，放行该 project 下所有 document
  // 即：父节点授权后，子孙节点默认全量放行
}

// ABAC scope 树：子节点可能有更深的约束（filter 闭包或嵌套 ID）
{
  "department": [
    {
      "id": 1,
      "project": [
        {"id": 1, "document": ScopeFilter(apply=...)},
        {"id": 2}
      ]
    }
  ]
  // project{1} 的 document 被 ScopeFilter 约束 → 只加载满足条件的 document
  // project{2} 的 document 无子约束 → 放行
}
```

RBAC 本质上每个类型只需要一层 ID 列表（用户能访问哪些 department、哪些 project），不需要按实例差异化约束子孙。但统一使用嵌套结构使得 Plugin 只需要一套传播逻辑，RBAC 只是"叶子节点为空对象"的特例。

### 3.3 Step 2：Scope 绑定到根对象

```python
# 类似 pagination 的 attach 方式
scope_tree = await permission_plugin.compute_scope(user_id, action, scope_desc)
object.__setattr__(root_instance, '_access_scope_tree', scope_tree)
```

### 3.4 Step 3-4：AutoLoad 自动约束 + Hook 传播

**分工明确：AutoLoad 负责约束 Loader，resolved_hooks 负责传播 scope 到子节点。**

```
AutoLoad 读 scope → 只加载 dept {1, 3}
  │
  ├─ dept{1} resolved → hook 传播子 scope { project: [{id:1,...}, {id:2}] } 到 dept{1}
  │   │
  │   ├─ AutoLoad 读 scope → 只加载 project {1, 2}
  │   │   │
  │   │   ├─ project{1} → hook 传播子 scope { document: [{id:1}, {id:2}] }
  │   │   │   └─ AutoLoad 读 scope → 只加载 document {1, 2}
  │   │   │
  │   │   └─ project{2} → 无子 scope → AutoLoad 正常加载
  │   │
  │   └─ ...
  │
  └─ dept{3} resolved → hook 传播子 scope { project: ScopeFilter(...) } 到 dept{3}
      └─ AutoLoad 读 scope → 通过 filter 约束加载
          └─ project{5} → hook 传播子 scope { document: [{id:7}] }
              └─ AutoLoad 读 scope → 只加载 document {7}
```

**执行时序（基于 resolver.py 源码）：**

```
_execute_resolve_method_field:
  1. resolve 方法执行（AutoLoad 生成的） → 返回结果
  2. resolved_hooks 执行（inject_access_scope） → 向结果注入子 scope
  3. _traverse 递归进入结果 → 子节点的 AutoLoad 读取注入的 scope
```

hook 在 `_traverse` 之前执行，子节点被 traverse 时 scope 已经就绪。这个时序保证 AutoLoad 在下一层能读到 scope。

---

## 四、注入机制：AutoLoad 约束 + resolved_hooks 传播

### 4.1 和 Pagination 的同构关系

pydantic-resolve 的 GraphQL 分页已验证了 resolved_hooks + 隐藏字段注入的模式：

```
Pagination：
  _collect_pagination_tree()    → 从 GraphQL 查询构建分页树
  注入根对象                     → object.__setattr__(inst, _pag_tree, tree)
  resolved_hooks                → inject_nested_pagination(parent, field, result)
  子节点读取                     → 从树上取 PageArgs
  约束 DataLoader               → PageLoadCommand(fk, page_args) 作为 key

权限 Plugin（基于 ER Diagram）：
  ER Diagram Relationship 链    → 自动推导层级描述
  权限系统返回                   → 树状 scope（ID / filter / 无约束）
  注入根对象                     → object.__setattr__(root, _access_scope_tree, tree)
  AutoLoad                      → 读取 scope，约束 Loader（ID 或 filter）
  resolved_hooks                → inject_access_scope(parent, field, result)（scope 传播）
  子节点                        → AutoLoad 读取注入的 scope，继续约束
```

### 4.2 Hook 实现——按 ID 匹配传播子 scope

Hook 不做过滤，只负责将 scope 树从 parent 传播到 resolved children。scope 树是 per-ID 的，需要按 item ID 匹配对应的子树：

```python
def inject_access_scope(parent, field_name, result):
    """
    resolved_hook: 将 scope 树从 parent 传播到 resolved children。
    约束由 AutoLoad 在下一层 resolve 时自动完成。
    """
    scope_tree = getattr(parent, '_access_scope_tree', None)
    if not scope_tree or field_name not in scope_tree:
        return

    child_scope = scope_tree[field_name]

    # 列表字段：按 item ID 匹配对应的子 scope
    items = getattr(result, 'items', None) or (result if isinstance(result, list) else None)
    if items:
        # scope 可能是 ID 列表或 ScopeFilter，ID 列表需要按 ID 匹配
        if isinstance(child_scope, list):
            scope_map = {
                s['id']: {k: v for k, v in s.items() if k != 'id'}
                for s in child_scope
            }
            for item in items:
                item_scope = scope_map.get(getattr(item, 'id', None))
                if item_scope:
                    object.__setattr__(item, '_access_scope_tree', item_scope)
        else:
            # ScopeFilter 或其他形态：直接注入给所有 items
            for item in items:
                object.__setattr__(item, '_access_scope_tree', child_scope)
        return

    # 单个对象
    if hasattr(result, '__dict__'):
        object.__setattr__(result, '_access_scope_tree', child_scope)
```

### 4.3 AutoLoad 自动约束（支持三种 scope 形态）

AutoLoad 执行 resolve 时，自动检查实例上的 `_access_scope_tree`：

```python
# AutoLoad 内部逻辑（伪代码）
def auto_load_resolve(self, loader):
    scope_tree = getattr(self, '_access_scope_tree', None)
    field_scope = scope_tree.get(self._relationship_name) if scope_tree else None

    if field_scope is None:
        # 无 scope 约束，正常加载
        return loader.load(self.id)

    if isinstance(field_scope, list):
        # 形态1：ID 列表 → 精确过滤
        allowed_ids = {item['id'] for item in field_scope}
        return loader.load_many(allowed_ids)

    if isinstance(field_scope, ScopeFilter):
        # 形态2：filter 闭包 → append 到 query
        return loader.load_with_filter(self.id, field_scope)
```

使用者不需要写任何 scope 相关代码，`AutoLoad()` 声明即可：

```python
class DeptView(DeptEntity):
    projects: Annotated[list[ProjectView], AutoLoad()] = []
    # AutoLoad 自动读取 _access_scope_tree 约束加载范围
```

### 4.4 GraphQL 和 REST 统一

```
GraphQL 路径和 REST/Resolver 路径最终都汇聚到：
  Resolver._execute_resolve_method_field()
    → resolved_hooks 循环

一个注入点，两种路径统一。
```

### 4.5 端到端调用示例

```python
# --- Phase 1: Entity + ER Diagram ---
class DeptEntity(BaseModel, BaseEntity):
    __relationships__ = [
        Relationship(fk='id', name='projects', target=list[ProjectEntity], loader=projects_loader)
    ]
    id: int
    name: str

class ProjectEntity(BaseModel, BaseEntity):
    __relationships__ = [
        Relationship(fk='id', name='documents', target=list[DocumentEntity], loader=documents_loader)
    ]
    id: int
    name: str
    dept_id: int

class DocumentEntity(BaseModel, BaseEntity):
    id: int
    title: str
    project_id: int

# --- Phase 3: API 响应 + 权限 Plugin ---

# 1. Plugin 初始化（从 ER Diagram 自动生成 scope_desc）
diagram = BaseEntity.get_diagram()
AutoLoad = diagram.create_auto_load()

plugin = PermissionPlugin(
    permission_service=my_permission_service,
    diagram=diagram,
)

# 2. FastAPI endpoint
@app.get("/departments")
async def list_departments(user_id: int = Depends(get_current_user_id)):
    # 2a. 计算 scope 树
    scope_tree = await plugin.compute_scope(user_id, "read")
    # scope_tree 示例:
    # {
    #   "department": [
    #     {"id": 1, "project": [{"id": 1}, {"id": 2}]},
    #     {"id": 3, "project": ScopeFilter(apply=lambda q: q.filter(Project.status == 'active'))}
    #   ]
    # }

    # 2b. 构建根对象并挂载 scope
    root = DepartmentListView(departments=[])
    object.__setattr__(root, '_access_scope_tree', scope_tree)

    # 2c. resolve（AutoLoad 自动约束 + hook 传播 scope）
    resolver = Resolver(resolved_hooks=[inject_access_scope])
    result = await resolver.resolve(root)
    return result

# 3. 响应模型
class DepartmentListView(BaseModel):
    departments: Annotated[list[DeptView], AutoLoad()] = []

class DeptView(DeptEntity):
    projects: Annotated[list[ProjectView], AutoLoad()] = []

class ProjectView(ProjectEntity):
    documents: Annotated[list[DocumentView], AutoLoad()] = []

class DocumentView(DocumentEntity):
    pass
```

---

## 五、各组件职责分工

```
┌──────────────────────────────────────────────────────────┐
│  Phase 3: 权限 Plugin + AutoLoad                          │
│                                                          │
│  Plugin:                                                  │
│  ① 从 ER Diagram 自动推导层级描述                         │
│  ② 调用权限系统，获取树状 scope                            │
│  ③ 将 scope 挂到根对象                                    │
│  ④ 注册 resolved_hook 用于 scope 传播                     │
│                                                          │
│  AutoLoad:                                                │
│  ⑤ 读取实例上的 _access_scope_tree                        │
│  ⑥ 根据 scope 形态（ID / filter / 无约束）约束 Loader     │
│                                                          │
│  resolved_hooks:                                          │
│  ⑦ 将子 scope 传播到 resolved children                    │
│                                                          │
│  Entity 不知道 │ Loader 不知道 │ 使用者不知道 │ 前端不知道 │
└──────────────────────────────────────────────────────────┘
```

Loader 接受 scope 约束，和接受 PageArgs 分页参数是同一件事——**都是获取数据时的范围限制，不感知来源。**

---

## 六、Scope 的三种形态与 ABAC 覆盖

### 6.1 后置过滤破坏分页

```
请求：GET /documents?page=1&limit=10

后置过滤（post_* 或 resolved_hooks 过滤）：
  DB 返回 10 条 → 过滤后剩 3 条 → 用户要 10 条只拿到 3 条
  total_count 不反映有权数据的真实数量
  has_more 无法判断（不知道后续页面还有没有有权的记录）
  → 分页的两个基石（总数、偏移）全部失效
```

后置过滤意味着权限判断在数据查询之后，分页器在查询时不知道哪些记录会被过滤掉。**Scope 预计算把权限从"查询后判断"变成"查询前已知"，是分页与权限共存的必要条件。**

### 6.2 Scope 的三种形态

ABAC 条件依赖资源属性，无法总是预计算为 ID 集合。Scope 支持三种形态，覆盖从精确到模糊的全部范围：

| scope 形态 | 含义 | AutoLoad / DataLoader 行为 |
|-----------|------|---------------------------|
| ID 列表 `[{id:1}, {id:2}]` | 精确允许的资源 | `WHERE id IN (1, 2)` |
| Filter 闭包 `ScopeFilter(apply=...)` | 规则覆盖大量资源 | 闭包 append 到 query |
| 无子节点 / `None` | 全量放行 | 正常加载，不约束 |

**Filter 以闭包形式传递，在权限系统内部捕获用户上下文：**

```python
# 权限系统内部，捕获 user context 创建闭包
def compute_scope(user, action, scope_desc):
    return {
        "document": ScopeFilter(
            apply=lambda q: q.filter(
                Document.classification_level <= user.clearance_level
            )
        )
    }

# DataLoader 端，只调用闭包，不知道 user context
def batch_load_fn(self, keys):
    query = session.query(Document).filter(Document.id.in_(keys))
    if scope_filter:
        query = scope_filter.apply(query)  # 闭包调用，user context 已封装在内
    return query.all()
```

- **DataLoader 不知道 user context**——闭包已捕获
- **类型安全**——用 ORM 方法而非裸 SQL，避免注入
- **可测试**——闭包可以独立测试
- **数据库无关**——闭包内部用 ORM 抽象，不绑定具体 SQL 方言

filter 来源不一定是权限——搜索条件、业务规则也可以复用同一机制。对 DataLoader 来说只是"支持条件过滤"这个通用能力。

**ScopeFilter 的限制：**
- **不跨进程**：闭包无法序列化，scope 树仅在单进程内使用。如果需要跨进程传递（如微服务架构），应使用 ID 列表形态而非 filter 闭包
- **DataLoader batching 兼容**：当 DataLoader 批量收到多个 key 时，同一批次内共享同一个 ScopeFilter（同一层级、同一权限规则），闭包对所有 key 统一 apply，不影响 batching 效率

### 6.3 ABAC 场景覆盖分析

权限系统内部将 RBAC/ABAC 规则翻译为对应的 scope 形态：

```
┌──────────────────────────────────────────────────┐
│  阶段一：权限系统（内部可以很复杂）                 │
│                                                  │
│  RBAC:  role → permission → 输出嵌套 ID 树（叶子无子约束）  │
│  ABAC:  用户属性 + 资源规则 → 输出嵌套 scope 树（含 filter）  │
│  管理员: 输出无约束                                           │
│                                                             │
│  不论内部怎么算，输出格式统一：嵌套 scope 树                    │
│  RBAC 和 ABAC 共用一套传播逻辑，RBAC 是"叶子为空"的特例        │
└──────────────────────┬───────────────────────────┘
                       │
          契约：输入 user_id + action + 层级描述
                输出 嵌套 scope 树（ID 列表 / filter 闭包 / 无约束）
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  阶段二：数据加载                                  │
│                                                  │
│  AutoLoad 读 scope → 根据 ID 或 filter 约束加载    │
│  DataLoader 支持 filter append → 通用能力，非权限   │
└──────────────────────────────────────────────────┘
```

| ABAC 场景 | 权限系统输出 | filter 能覆盖 |
|-----------|-------------|--------------|
| 部门归属 | ID 列表 或 filter 闭包 | 能 |
| 资源密级 | `ScopeFilter(apply=lambda q: q.filter(level <= user.clearance))` | 能 |
| 所有者 | `ScopeFilter(apply=lambda q: q.filter(created_by == user.id))` | 能 |
| 审批状态流转 | 复杂 OR 条件闭包 | 能，但复杂 |
| 时间窗口 | `ScopeFilter(apply=lambda q: q.filter(effective_date <= func.now()))` | 能 |
| 地域合规 | 非 EU 用户：filter 闭包；EU 用户：无约束 | 能 |
| 跨数据源判断 | 需要外部 RPC → 无法编译为 filter | 不能，降级为后置过滤 |
| 非 SQL 的 Python 逻辑 | 无法编译为 SQL/ORM 操作 | 不能，降级为后置过滤 |
| 动态配额 | 运行时状态，scope 无法预知 | 不能，降级为后置过滤 |

**filter 方案覆盖约 85% 的 ABAC 场景**，剩余场景降级为后置过滤（接受不分页的限制），或由权限系统内部预查询外部系统后将结果转为 ID 列表。

---

## 七、可参考的系统

| 系统 | 参考点 | 局限 |
|------|--------|------|
| **Google Zanzibar / SpiceDB** | 关系遍历、LookupResources 反向展开 scope | 输出扁平 ID，不保留层级 |
| **Hasura** | 权限规则编译成 SQL WHERE | 无层级继承展开 |
| **OPA Partial Evaluation** | 策略编译成查询约束 | 不知业务树结构 |
| **AWS IAM** | Deny 优先 + 通配符继承 | 扁平评估，不做树合并 |

**创新点**：Zanzibar 的关系遍历 + Hasura 的约束编译 + OPA 的策略求值，三者结合，通过 pydantic-resolve 的 resolved_hooks 约束 DataLoader。

---

## 八、待解决的问题

1. **权限树未覆盖分支的处理**：scope 只包含有显式授权的分支，未覆盖的部分默认拒绝还是放行
2. ~~**Loader key 替换的时机**~~：已决——AutoLoad 自动读取 scope 约束 Loader，不需要手动处理
3. **scope 缓存**：同一用户短时间内的 scope 可复用
4. **Allow/Deny 跨层级传播**：树上某节点的 deny 如何截断子节点的 allow

---

## 九、现有参考实现

- `demo/rbac/` — 现有 RBAC/ABAC demo（ancestor tracing + ABAC condition + mail group inheritance）
  - 使用 post_* 后置过滤，非 scope 预计算
  - 后续将升级为 scope 预计算模式
- `pydantic_resolve/graphql/pagination/` — 分页注入机制（scope 的同构参考）
  - `injector.py`：inject_nested_pagination 的实现
  - `types.py`：PageArgs / PageLoadCommand 的定义
