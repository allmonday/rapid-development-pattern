# Mutation 实现测试指南

## 实现概览

已成功为项目添加 **17 个 GraphQL mutation 方法**，遵循 DDD 聚合根模式：

### 实现的 Mutation 方法

#### User 模块 (3 个)
- `createUser(name: String!, level: String): User!`
- `updateUser(id: Int!, name: String, level: String): User`
- `deleteUser(id: Int!): Boolean!`

#### Team 模块 (7 个)
- `createTeam(name: String!): Team!`
- `updateTeam(id: Int!, name: String): Team`
- `deleteTeam(id: Int!): Boolean!`
- `createSprint(teamId: Int!, name: String!, status: String): Sprint!`
- `deleteSprint(id: Int!): Boolean!`
- `addTeamMember(teamId: Int!, userId: Int!): Boolean!`
- `removeTeamMember(teamId: Int!, userId: Int!): Boolean!`

#### Sprint 模块 (3 个)
- `updateSprint(id: Int!, name: String, status: String): Sprint`
- `createStory(sprintId: Int!, name: String!, ownerId: Int!): Story!`
- `deleteStory(id: Int!): Boolean!`

#### Story 模块 (3 个)
- `updateStory(id: Int!, name: String, ownerId: Int): Story`
- `createTask(storyId: Int!, name: String!, ownerId: Int!, estimate: Int): Task!`
- `deleteTask(id: Int!): Boolean!`

#### Task 模块 (1 个)
- `updateTask(id: Int!, name: String, ownerId: Int, estimate: Int): Task`

## 测试步骤

### 1. 启动服务器

```bash
uv run uvicorn src.main:app --reload
```

### 2. 访问 GraphiQL

打开浏览器访问：http://localhost:8000/graphql

### 3. 测试 Mutation 操作

#### 测试 1: 创建用户

```graphql
mutation {
  createUser(name: "Alice", level: "admin") {
    id
    name
    level
  }
}
```

#### 测试 2: 创建团队

```graphql
mutation {
  createTeam(name: "Backend Team") {
    id
    name
  }
}
```

#### 测试 3: 创建 Sprint (由 Team 负责)

```graphql
mutation {
  createSprint(teamId: 1, name: "Sprint 1", status: "planning") {
    id
    name
    status
    team {
      id
      name
    }
  }
}
```

#### 测试 4: 创建 Story (由 Sprint 负责)

```graphql
mutation {
  createStory(sprintId: 1, name: "User Login Feature", ownerId: 1) {
    id
    name
    owner {
      id
      name
    }
    sprint {
      id
      name
    }
  }
}
```

#### 测试 5: 创建 Task (由 Story 负责)

```graphql
mutation {
  createTask(storyId: 1, name: "Implement API", ownerId: 1, estimate: 8) {
    id
    name
    estimate
    owner {
      name
    }
    story {
      name
    }
  }
}
```

#### 测试 6: 更新 Sprint

```graphql
mutation {
  updateSprint(id: 1, name: "Sprint 1 - Updated", status: "active") {
    id
    name
    status
  }
}
```

#### 测试 7: 更新 Story

```graphql
mutation {
  updateStory(id: 1, name: "Updated Story Name") {
    id
    name
  }
}
```

#### 测试 8: 更新 Task

```graphql
mutation {
  updateTask(id: 1, estimate: 16) {
    id
    name
    estimate
  }
}
```

#### 测试 9: 添加团队成员

```graphql
mutation {
  addTeamMember(teamId: 1, userId: 2)
}
```

#### 测试 10: 删除操作

```graphql
mutation {
  deleteTask(id: 1)
  deleteStory(id: 1)
  deleteSprint(id: 1)
  deleteTeam(id: 1)
  deleteUser(id: 1)
}
```

### 4. 查看 Schema

访问 http://localhost:8000/schema 查看完整的 GraphQL Schema SDL

### 5. 验证生命周期

完整的 CRUD 生命周期测试：

```graphql
mutation {
  # 1. 创建用户
  user: createUser(name: "Test User", level: "user") {
    id
    name
  }

  # 2. 创建团队
  team: createTeam(name: "Test Team") {
    id
    name
  }

  # 3. 创建 Sprint
  sprint: createSprint(teamId: 1, name: "Test Sprint") {
    id
    name
  }

  # 4. 创建 Story
  story: createStory(sprintId: 1, name: "Test Story", ownerId: 1) {
    id
    name
  }

  # 5. 创建 Task
  task: createTask(storyId: 1, name: "Test Task", ownerId: 1) {
    id
    name
  }
}
```

## 预期结果

✅ 所有 mutation 操作应该成功执行
✅ 创建操作返回创建的实体对象
✅ 更新操作返回更新后的实体对象（或 null 如果实体不存在）
✅ 删除操作返回 Boolean 表示是否成功
✅ GraphQL Schema 应该包含所有 17 个 mutation
✅ 关联数据（如 owner, team 等）应该正确加载

## 文件变更总结

### 新增文件 (5 个)
- `src/services/user/mutation.py`
- `src/services/team/mutation.py`
- `src/services/sprint/mutation.py`
- `src/services/story/mutation.py`
- `src/services/task/mutation.py`

### 修改文件 (5 个)
- `src/services/user/schema.py`
- `src/services/team/schema.py`
- `src/services/sprint/schema.py`
- `src/services/story/schema.py`
- `src/services/task/schema.py`

## 架构特点

1. **DDD 聚合根模式**：User 和 Team 作为聚合根，拥有完整的 CRUD 权限
2. **父节点管理子节点**：子实体的创建和删除由父节点负责
3. **自身负责更新**：所有实体都可以更新自己的属性
4. **清晰的分层**：mutation.py 负责数据库操作，schema.py 负责 GraphQL 接口
5. **类型安全**：完整的类型提示，自动生成 GraphQL Schema
