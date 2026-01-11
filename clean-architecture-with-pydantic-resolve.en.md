# Clean Architecture Practice with Pydantic-Resolve and FastAPI-Voyager

> A Python web development methodology for complex business scenarios

## Table of Contents

- [Clean Architecture Practice with Pydantic-Resolve and FastAPI-Voyager](#clean-architecture-practice-with-pydantic-resolve-and-fastapi-voyager)
  - [Table of Contents](#table-of-contents)
  - [1. Background and Problems](#1-background-and-problems)
    - [1.1 Current Mainstream Approaches and Their Pain Points](#11-current-mainstream-approaches-and-their-pain-points)
      - [Approach 1: Using ORM Directly (e.g., SQLAlchemy)](#approach-1-using-orm-directly-eg-sqlalchemy)
      - [Approach 2: Using ORM Eager Loading](#approach-2-using-orm-eager-loading)
      - [Approach 3: Manual Data Assembly](#approach-3-manual-data-assembly)
      - [Approach 4: Using GraphQL](#approach-4-using-graphql)
    - [1.2 Root Cause Analysis](#12-root-cause-analysis)
      - [Problem 1: Confusion Between Business Model and Data Model](#problem-1-confusion-between-business-model-and-data-model)
      - [Problem 2: Wrong Dependency Direction](#problem-2-wrong-dependency-direction)
      - [Problem 3: Lack of Explicit Business Relationship Declarations](#problem-3-lack-of-explicit-business-relationship-declarations)
      - [Problem 4: Technical Exposure of Intermediate Tables](#problem-4-technical-exposure-of-intermediate-tables)
  - [2. Clean Architecture Principles](#2-clean-architecture-principles)
    - [2.1 Core Principles](#21-core-principles)
      - [Principle 1: Dependency Rule](#principle-1-dependency-rule)
      - [Principle 2: Business Rules Independence](#principle-2-business-rules-independence)
      - [Principle 3: Data Transfer Across Boundaries](#principle-3-data-transfer-across-boundaries)
    - [2.2 Dependency Rules](#22-dependency-rules)
    - [2.3 Application in Web Development](#23-application-in-web-development)
      - [Problems with Traditional Architecture](#problems-with-traditional-architecture)
  - [3. Pydantic-Resolve: The Business Model Layer](#3-pydantic-resolve-the-business-model-layer)
    - [3.1 Core Concepts](#31-core-concepts)
      - [Core Philosophy](#core-philosophy)
    - [3.2 ERD: Declaring Business Relationships](#32-erd-declaring-business-relationships)
      - [Defining Entity Relationship Diagram](#defining-entity-relationship-diagram)
      - [Key Features of ERD](#key-features-of-erd)
    - [3.3 DataLoader: The Secret of Batch Loading](#33-dataloader-the-secret-of-batch-loading)
      - [Problem: N+1 Queries](#problem-n1-queries)
      - [Solution: DataLoader](#solution-dataloader)
      - [DefineSubset: Field Selection and Reuse](#definesubset-field-selection-and-reuse)
    - [3.4 Resolve and Post: Data Assembly and Computation](#34-resolve-and-post-data-assembly-and-computation)
      - [Resolve: Declaring Data Dependencies](#resolve-declaring-data-dependencies)
      - [Post: Data Post-processing](#post-data-post-processing)
    - [3.5 Cross-Layer Data Transfer](#35-cross-layer-data-transfer)
      - [Expose: Parent Exposes Data to Children](#expose-parent-exposes-data-to-children)
      - [Collect: Parent Collects Data from Children](#collect-parent-collects-data-from-children)
    - [3.6 Summary](#36-summary)
  - [4. FastAPI-Voyager: Architecture Visualization](#4-fastapi-voyager-architecture-visualization)
    - [4.0 Why Architecture Visualization?](#40-why-architecture-visualization)
    - [4.1 Core Features](#41-core-features)
      - [1. Automatic API Structure Scanning](#1-automatic-api-structure-scanning)
      - [2. Three-Layer Architecture Display](#2-three-layer-architecture-display)
    - [4.2 Combining ERD with API Routes](#42-combining-erd-with-api-routes)
      - [Core: Business-Technical Mapping](#core-business-technical-mapping)
    - [4.3 Practical Application Scenarios](#43-practical-application-scenarios)
      - [Scenario 1: Discovering Architecture Drift](#scenario-1-discovering-architecture-drift)
      - [Scenario 2: Discovering Excessive Nesting](#scenario-2-discovering-excessive-nesting)
      - [Scenario 3: Quick Onboarding for New Team Members](#scenario-3-quick-onboarding-for-new-team-members)
  - [5. Complete Development Workflow](#5-complete-development-workflow)
    - [5.1 Architecture Design Phase](#51-architecture-design-phase)
      - [Step 1: Identify Core Business Entities](#step-1-identify-core-business-entities)
      - [Step 2: Define Entity Relationships](#step-2-define-entity-relationships)
    - [5.2 Entity Definition Phase](#52-entity-definition-phase)
      - [Define ERD](#define-erd)
    - [5.3 Data Layer Implementation](#53-data-layer-implementation)
      - [Define ORM Models (Guided by ERD)](#define-orm-models-guided-by-erd)
      - [Implement Loaders](#implement-loaders)
    - [5.4 API Implementation Phase](#54-api-implementation-phase)
      - [Define Response Models](#define-response-models)
      - [Implement API Routes](#implement-api-routes)
    - [5.5 Visualization Verification](#55-visualization-verification)
      - [Integrate FastAPI-Voyager](#integrate-fastapi-voyager)
      - [Verify Architecture](#verify-architecture)
  - [6. Comparison with Other Approaches](#6-comparison-with-other-approaches)
    - [6.1 vs Traditional ORM](#61-vs-traditional-orm)
    - [6.2 vs GraphQL](#62-vs-graphql)
    - [6.3 vs DDD Frameworks](#63-vs-ddd-frameworks)
  - [7. Conclusion](#7-conclusion)
    - [Core Values](#core-values)
      - [1. Business Model First](#1-business-model-first)
      - [2. Clean Architecture Implementation](#2-clean-architecture-implementation)
      - [3. Automatic Performance Optimization](#3-automatic-performance-optimization)
      - [4. Architecture Visualization](#4-architecture-visualization)
      - [5. Development Efficiency Improvement](#5-development-efficiency-improvement)
      - [6. Easier Testing and Debugging](#6-easier-testing-and-debugging)
    - [Applicable Scenarios](#applicable-scenarios)
      - [Recommended Use Cases](#recommended-use-cases)
      - [Not Recommended Use Cases](#not-recommended-use-cases)
    - [Closing Remarks](#closing-remarks)
  - [References](#references)

---

## Preface

When dealing with complex business scenarios in Python web development, developers often face a dilemma: traditional ORM approaches are intuitive but prone to N+1 query problems, while GraphQL is flexible and powerful but has a steep learning curve and is difficult to optimize. More importantly, issues like the confusion between business models and data models, and incorrect dependency directions, lead to unmaintainable code where business logic gets hijacked by implementation details.

This article presents a Clean Architecture practice based on **Pydantic-Resolve** and **FastAPI-Voyager**. The core philosophy of this approach is: **"Let code reflect business, not make business adapt to code."** By using ERD (Entity Relationship Diagram) to explicitly declare business relationships, we achieve decoupling of business models from technical implementation. DataLoader automatically handles batch loading, transparently solving performance issues. FastAPI-Voyager visualizes the architecture, making the boundary between business models and use cases clearly visible.

Starting from an analysis of root problems, this article explores Clean Architecture's dependency rules in depth, explains Pydantic-Resolve's core concepts (ERD, DataLoader, Resolve/Post, Expose/Collect, etc.), and demonstrates a complete development workflow. Whether you're looking for a GraphQL alternative or hoping to improve your existing project's architecture, you'll find valuable insights here.

---

## 1. Background and Problems

### 1.1 Current Mainstream Approaches and Their Pain Points

In Python web development, when dealing with complex business scenarios, developers typically adopt several approaches:

#### Approach 1: Using ORM Directly (e.g., SQLAlchemy)

```python
@router.get("/teams/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # Get team basic information
    team = await session.get(Team, team_id)

    # Get Sprint list
    sprints = await session.execute(
        select(Sprint).where(Sprint.team_id == team_id)
    )
    team.sprints = sprints.scalars().all()

    # Get each Sprint's Story
    for sprint in team.sprints:
        stories = await session.execute(
            select(Story).where(Story.sprint_id == sprint.id)
        )
        sprint.stories = stories.scalars().all()

        # Get each Story's Task
        for story in sprint.stories:
            tasks = await session.execute(
                select(Task).where(Task.story_id == story.id)
            )
            story.tasks = tasks.scalars().all()

            # Get each Task's owner
            for task in story.tasks:
                task.owner = await session.get(User, task.owner_id)

    return team
```

This approach is indeed intuitive in simple scenarios and allows for quick start. The type-safety of ORM can catch some errors at compile time, and the one-to-one correspondence with database table structures makes the code easy to understand. However, when facing real business scenarios, the limitations of this approach become quickly apparent.

The most critical issue is the N+1 query problem. Although the code looks clean, it generates a large number of database queries during execution. Each time we access an association, the ORM initiates a new query. In deeply nested scenarios, the number of queries grows exponentially. Worse still, these performance issues are not easily discovered during development and only become apparent after data accumulates to a certain level, by which time it's often too late.

Code organization is also problematic. Data fetching logic is scattered across nested loops, mixing business logic with data fetching logic, making it hard to read and maintain. When business rules need to be modified, developers have to locate modification points within complex nested structures, easily introducing new bugs. Performance is also uncontrollable, degrading drastically as data volume grows, and these bottlenecks are difficult to observe directly at the code level.

Furthermore, similar data fetching logic appears repeatedly across multiple APIs, leading to significant code duplication. When one API needs "team and its sprints" and another needs "team and its members," even if their query logic is very similar, they must be written separately. This violates the DRY (Don't Repeat Yourself) principle and increases maintenance costs.

#### Approach 2: Using ORM Eager Loading

```python
@router.get("/teams/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # Use joinedload to preload associated data
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

To solve the N+1 query problem, ORM provides Eager Loading mechanisms, allowing us to preload associated data through `joinedload`, `selectinload`, and similar methods. The code becomes more concise, and performance issues are alleviated. However, this approach introduces new challenges.

The most obvious issue is the Cartesian product. When we use multi-level JOINs to preload associated data, the amount of data returned by the database expands dramatically. For example, if a team has 10 sprints, each sprint has 10 stories, and each story has 10 tasks, the JOIN result set will contain 1000 rows. Even if each row's data volume is small, this puts pressure on network transmission and memory usage.

More serious is the lack of flexibility. Eager Loading strategies are hardcoded in the application, and all APIs using the same Model will execute the same preloading logic. However, different APIs often need different data. One API might only need team basic information, another needs the team's sprints, and yet another needs the team's members. If we uniformly use Eager Loading to load all associated data, we encounter the over-fetching problem—data not needed by the frontend is still queried and transmitted, wasting resources.

Configuring Eager Loading is itself complex. Developers need to understand the differences between various loading strategies like `lazy`, `joinedload`, `selectinload`, `subquery`, knowing when to use which and what side effects each might have. Such configuration errors can easily lead to performance issues or unexpected data loading behavior. Moreover, this "one-size-fits-all" configuration means all APIs use the same loading strategy, making it impossible to optimize for specific scenarios.

#### Approach 3: Manual Data Assembly

```python
@router.get("/teams/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # 1. Batch fetch all required data
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

    # 2. Manually assemble data structure
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

To achieve optimal performance and precise data control, experienced developers choose to manually assemble data. This approach provides complete control over query logic, allowing precise control of each query's SQL statement and avoiding unnecessary database access. Through batch queries and intelligent data assembly, we can achieve optimal performance without redundant data.

However, the cost is that the code becomes very verbose. As shown in the example above, to retrieve complete information about a team, we need to write multiple queries, manually build data dictionaries, and then assemble data through nested loops. Both code length and complexity increase significantly, while the code that truly expresses business logic gets buried in data assembly details.

Greater error proneness is also a major issue. Manual data assembly involves numerous indexing operations and nested loops, making it easy to introduce indexing errors, null reference exceptions, and other bugs. These errors often only manifest at runtime with specific data conditions, making them hard to discover during development.

Maintenance costs are even higher. When business rules change (e.g., needing to add a new association), developers must modify data assembly logic in all related APIs. Missing a spot leads to data inconsistency. Moreover, similar data assembly logic appears repeatedly across multiple APIs, violating the DRY principle.

The most fundamental problem is that this code has become purely a data handler, showing no business intent. The code is filled with dictionary operations, nested loops, and index lookups—all technical details unrelated to business requirements. New team members can hardly understand business logic from this code, making knowledge transfer exceptionally difficult.

#### Approach 4: Using GraphQL

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

GraphQL is indeed an attractive solution. The frontend can fetch data on demand, querying only the fields needed, without over-fetching. It provides a type-safe query interface and can automatically solve N+1 query problems through DataLoader. These features make GraphQL popular in frontend development.

However, GraphQL's learning curve is very steep. Developers need to learn a brand-new query language, Schema definition, Resolver writing, DataLoader configuration, and a pile of other concepts—forming a sharp contrast with REST API's intuitiveness. More troublesome is that GraphQL's excessive flexibility brings huge challenges to the backend. The frontend can construct arbitrarily complex queries, some perhaps never even imagined by the developer, making it difficult for the backend to perform targeted optimization. When a query is nested 10 levels deep and returns millions of data rows, both database and server face tremendous pressure.

Debugging GraphQL APIs is also much more complex than debugging REST APIs. When a GraphQL query errors out, error messages are often hard to trace back to the specific problem source. Moreover, GraphQL requires additional server and toolchain support and cannot directly leverage the existing FastAPI ecosystem. Features like FastAPI's dependency injection, middleware, and automatic documentation generation are all unavailable in GraphQL.

There's also a deeper issue: the blurred boundary between ERD and use cases. GraphQL's Schema plays two roles simultaneously: entity model and query interface. When designing a GraphQL Schema, it's hard to determine whether to organize by entity (one Type per database table) or by use case (different business scenarios need different fields). This leads to unclear best practices, with different projects and developers having completely different organizational approaches.

Furthermore, as business grows, all use cases get piled into the same Schema, causing Schema bloat and making it hard to maintain. Access control also becomes exceptionally complex. Different API endpoints might have different permission requirements, but they all query the same entity (e.g., User), making it difficult in GraphQL to apply different permission rules for different query scenarios.

### 1.2 Root Cause Analysis

All the approaches we discussed above, while their surface problems differ, share the same core dilemma.

#### Problem 1: Confusion Between Business Model and Data Model

```python
# SQLAlchemy ORM plays two roles simultaneously:
# 1. Data model (how to store)
# 2. Business model (business concept)

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Is this a database foreign key relationship, or a business relationship?
    sprints = relationship("Sprint", back_populates="team")
```

In traditional ORM development, business model and data model are mixed together. Look at this example: the `Team` class expresses both a business concept (what a team is) and carries data model details (how it's stored in the database). When we define `relationship` on the `sprints` field, are we describing a business relationship (team has multiple sprints) or declaring a database foreign key constraint? This ambiguity leads to many problems.

Database design constraints directly affect our business modeling. For example, if the `teams` table in the database doesn't have a direct foreign key to `users`, but instead relates through an intermediate table `team_members`, then in the ORM we must also define the relationship through this intermediate table. This means business models are forced to adapt to database implementation details, not the other way around.

More seriously, this approach cannot express cross-database, cross-service business relationships. In modern systems, data might be distributed across different databases, or even stored in external services. For example, user basic information is in PostgreSQL, user preferences are in MongoDB, and user real-time status is in Redis. ORM's `relationship` cannot cross these boundaries, thus business models get limited to the scope of a single database.

#### Problem 2: Wrong Dependency Direction

```
Traditional architecture dependency direction:
┌─────────────┐
│   API Layer │  ← depends on
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ ORM Models  │  ← depends on
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Database   │
└─────────────┘

Problem: Business rules depend on database implementation!
```

This violates Clean Architecture's dependency rule. The correct dependency relationship should be: business rules are most stable, not depending on any outer layer; databases are implementation details and should depend on business rules; when databases change, business rules should not be affected. Traditional architecture's dependency direction is precisely opposite—business rules get hijacked by database implementation details.

#### Problem 3: Lack of Explicit Business Relationship Declarations

```python
# Traditional approach: business relationships hidden in queries
async def get_team_tasks(team_id: int):
    # "Team's tasks" business concept hidden in SQL WHERE
    result = await session.execute(
        select(Task)
        .join(Sprint, Sprint.id == Task.sprint_id)
        .where(Sprint.team_id == team_id)
    )
    return result.scalars().all()
```

Business relationships are not explicitly declared—this is a very hidden but harmful problem. Look at this example: "team's tasks" is a clear business concept, but this concept is hidden in SQL's JOIN and WHERE clauses. New team members need to read a lot of code to understand what business relationships exist in the system and how they're defined. Worse still, there's no automated way to check business relationship consistency. When requirements change and a relationship needs modification, developers can hardly find all related code, easily missing spots and leading to business logic inconsistency.

#### Problem 4: Technical Exposure of Intermediate Tables

In SQLAlchemy ORM, many-to-many relationships require explicit definition of intermediate tables, causing technical details to leak into the business layer.

```python
# SQLAlchemy ORM: must define intermediate table
class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # ORM relationship needs to specify intermediate table
    members = relationship("User",
                          secondary="team_members",  # must specify intermediate table
                          back_populates="teams")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    teams = relationship("Team",
                        secondary="team_members",  # must specify intermediate table
                        back_populates="members")

# Intermediate table (technical implementation detail)
class TeamMember(Base):
    __tablename__ = 'team_members'
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String)  # possibly additional fields

# Query must care about intermediate table's existence
@router.get("/teams/{team_id}")
async def get_team_members(team_id: int, session: AsyncSession):
    # must query through intermediate table
    result = await session.execute(
        select(User)
        .join(TeamMember, TeamMember.user_id == User.id)  # intermediate table exposed
        .where(TeamMember.team_id == team_id)
    )
    return result.scalars().all()
```

The root of this problem is that ORM's many-to-many relationships require explicit definition of intermediate tables, causing technical details to leak directly into business layer code. Business code must know about the existence of the `team_members` intermediate table, and queries must explicitly join this intermediate table. This increases code complexity, and more importantly, business logic gets hijacked by database implementation details.

A deeper issue is that business semantics become blurred. Is `TeamMember` a meaningful business concept or purely a technical implementation? If the intermediate table has additional fields (e.g., `role` representing the user's role in the team, `joined_at` representing join time), should these fields be modeled as independent entities? Different developers might give different answers, lacking unified guiding principles.

Data assembly thus becomes complex. Querying "all members of a team" requires joining the intermediate table, and querying "teams a user belongs to" also requires joining the intermediate table. All queries involving many-to-many relationships become verbose and hard to understand. When business rules require "getting user's roles in all teams," the situation becomes even more complex. These technical details make implementing business logic exceptionally heavy.

**Contrast: Pydantic-Resolve ERD Approach**

```python
# ERD: business concepts clear, no need to care about intermediate tables
class TeamEntity(BaseModel, BaseEntity):
    """Team entity - business concept"""
    __relationships__ = [
        # directly express "team has multiple members" business relationship
        Relationship(
            field='id',
            target_kls=list[UserEntity],
            loader=team_to_users_loader  # loader handles intermediate table internally
        ),
    ]
    id: int
    name: str

class UserEntity(BaseModel, BaseEntity):
    """User entity - business concept"""
    __relationships__ = [
        # directly express "user belongs to multiple teams" business relationship
        Relationship(
            field='id',
            target_kls=list[TeamEntity],
            loader=user_to_teams_loader
        ),
    ]
    id: int
    name: str

# Loader implementation details: intermediate table only appears here
async def team_to_users_loader(team_ids: list[int]):
    """load team members - handle intermediate table internally"""
    async with get_session() as session:
        # only here needs to know about intermediate table's existence
        result = await session.execute(
            select(User)
            .join(TeamMember, TeamMember.user_id == User.id)
            .where(TeamMember.team_id.in_(team_ids))
        )
        users = result.scalars().all()

        # build mapping
        users_by_team = {}
        for user in users:
            for tm in user.team_memberships:
                if tm.team_id not in users_by_team:
                    users_by_team[tm.team_id] = []
                users_by_team[tm.team_id].append(user)

        return [users_by_team.get(tid, []) for tid in team_ids]
```

**Key Differences**:

| Dimension | SQLAlchemy ORM | Pydantic-Resolve ERD |
|------|----------------|---------------------|
| **Intermediate table location** | Exposed in business layer | Hidden in loader implementation |
| **Business semantics** | Technical relationship (`secondary`) | Business relationship (`team contains members`) |
| **Query code** | Need to join intermediate table | `loader.load(team_id)` |
| **Code location** | Scattered across places | Centralized in loader |
| **Testing** | Depends on database table structure | Can mock loader |

**Architecture Advantages**:

```
Traditional approach:
Team → TeamMember (intermediate table) → User
Business layer needs to know about intermediate table's existence

Pydantic-Resolve approach:
Team → User (business relationship)
Intermediate table is data layer implementation detail, business layer doesn't care
```

This means:

1. **Pure business model**: Team and User relationships directly express business semantics
2. **Technical detail encapsulation**: intermediate table's existence is encapsulated in loader
3. **Flexible storage strategy**:
   - Database can use intermediate table implementation
   - Or use JSON field storage
   - Or even external service (e.g., LDAP)
   - Business layer code needs no modification
4. **Easy to understand**: new people see ERD and understand business relationships, no need to first learn database design

---

## 2. Clean Architecture Principles

### 2.1 Core Principles

Clean Architecture was proposed by Robert C. Martin (Uncle Bob), with the core idea:

> **"Software architecture is the art of drawing lines that I call boundaries."**

#### Principle 1: Dependency Rule

```
Outer layers depend on inner layers, inner layers don't depend on outer layers.

                ↓ dependency direction
    ┌─────────────────────┐
    │   Frameworks &      │  outer layer
    │   Drivers           │  (implementation details)
    ├─────────────────────┤
    │   Interface         │
    │   Adapters          │
    ├─────────────────────┤
    │   Use Cases         │
    │   (Application)     │
    ├─────────────────────┤
    │   Entities          │  inner layer
    │   (Business Rules)  │  (core)
    └─────────────────────┘
```

Following the dependency rule requires attention to several key points. First, inner layers don't know about outer layers' existence—this means core business logic doesn't depend on any framework, database, or UI details. Second, inner layers don't contain outer layer information—for example, business rules shouldn't know whether data is stored with PostgreSQL or MongoDB. Finally, outer layer implementations can be replaced at any time without affecting inner layers—this means we can switch from SQLAlchemy to MongoDB, or from FastAPI to Django, without modifying business logic code.
#### Principle 2: Business Rules Independence

```python
# ❌ Wrong: business rules depend on database
class Task:
    def calculate_priority(self, session):
        # business logic contaminated by database implementation details
        if self.assignee_id in session.query(TeamMember).filter_by(role='lead'):
            return 'high'

# ✅ Right: business rules independent
class Task:
    def calculate_priority(self, assignee_roles):
        # business logic only depends on business concepts
        if 'lead' in assignee_roles:
            return 'high'
```

#### Principle 3: Data Transfer Across Boundaries

```python
# inner layer defines data structure
class TaskEntity(BaseModel):
    id: int
    name: str
    assignee_id: int

# outer layer responsible for conversion
def task_entity_to_orm(entity: TaskEntity) -> Task:
    return Task(
        id=entity.id,
        name=entity.name,
        assignee_id=entity.assignee_id
    )
```

### 2.2 Dependency Rules

In web development, dependency rules can be understood as follows:

```
┌────────────────────────────────────────────────────┐
│         Presentation Layer (outer)                 │
│  - FastAPI Routes                                   │
│  - Request/Response Models                          │
│  - depends on: Application Layer                    │
└────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│      Application Layer (Use Cases)                 │
│  - business use cases (get user, create order)     │
│  - depends on: Domain Layer                         │
└────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│           Domain Layer (inner)                      │
│  - Entities (business entities)                     │
│  - Business Rules (business rules)                 │
│  - Value Objects (value objects)                    │
│  - doesn't depend on any outer layer               │
└────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│    Infrastructure Layer (outermost)                 │
│  - Database (SQLAlchemy)                            │
│  - External Services                                │
│  - File System                                      │
└────────────────────────────────────────────────────┘
```

**Key insights**:
- **Entities shouldn't know about SQLAlchemy's existence**
- **Business Rules shouldn't know about database table structures**
- **Use Cases shouldn't know about HTTP protocol details**

### 2.3 Application in Web Development

#### Problems with Traditional Architecture

```python
# Traditional approach: all layers coupled

# Domain Layer (should be independent, but depends on ORM)
class User(Base):  # ← SQLAlchemy Base
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

# Application Layer (should only depend on Domain, but directly uses ORM)
async def create_user(data: dict, session: AsyncSession):
    user = User(**data)  # ← directly uses ORM Model
    session.add(user)
    await session.commit()

# Presentation Layer
@router.post("/users")
async def api_create_user(data: dict, session=Depends(get_session)):
    return await create_user(data, session)  # ← exposes database details
```

This code reveals the core problem of traditional architecture. Although SQLAlchemy establishes object-relational mapping (ORM) allowing database tables to be manipulated through Python objects, this mapping relationship is too tight. ORM Model bears both the responsibility of data persistence and the expression of business concepts, preventing objects from freely representing business models. Business entities get hijacked by database implementation details—every field and every relationship must correspond one-to-one with database table structures, completely losing freedom as independent business concepts.

Deeper problems include:

1. **Domain Layer bound to SQLAlchemy**: business entities inherit from SQLAlchemy's Base and cannot exist independently of the database
2. **Business logic cannot be tested without database**: writing unit tests requires starting a complete database environment, significantly reducing testing efficiency
3. **Switching databases requires modifying all layers**: when migrating from PostgreSQL to MongoDB, all code using ORM Models needs rewriting

---

## 3. Pydantic-Resolve: The Business Model Layer

### 3.1 Core Concepts

Pydantic-Resolve is a data assembly tool based on Pydantic that allows you to build complex data structures in a **declarative** manner.

#### Core Philosophy

> **"Describe what you want, not how to fetch it"**

```python
# ❌ Imperative: how to fetch
async def get_teams_with_tasks():
    teams = await get_teams()
    for team in teams:
        team.tasks = await get_tasks_by_team(team.id)  # N+1 problem
        for task in team.tasks:
            task.owner = await get_user(task.owner_id)  # N+1 again
    return teams

# ✅ Declarative: what you want
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

# usage
teams = await query_teams_from_db()
result = await Resolver().resolve(teams)
```

The essential difference between these two approaches lies in their focus. The imperative approach focuses on "how to fetch"—developers manually write data fetching logic, easily leading to N+1 query problems. The declarative approach focuses on "what you want"—by describing data structure to declare dependencies, while the framework automatically handles the actual data fetching logic. This simplifies code while avoiding performance traps.

### 3.2 ERD: Declaring Business Relationships

#### Defining Entity Relationship Diagram

```python
from pydantic_resolve import base_entity, Relationship, MultipleRelationship, Link, config_global_resolver

# 1. create BaseEntity
BaseEntity = base_entity()

# 2. define business entities
class UserEntity(BaseModel, BaseEntity):
    """User entity - business concept"""
    __relationships__ = [
        # multiple business relationships from same field 'id' to same target type
        MultipleRelationship(
            field='id',
            target_kls=list[TaskEntity],
            links=[
                Link(biz='created', loader=user_to_created_tasks_loader),
                Link(biz='assigned', loader=user_to_assigned_tasks_loader),
            ]
        ),
        # user's teams
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
    """Task entity - business concept"""
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

# 3. register ERD
diagram = BaseEntity.get_diagram()
config_global_resolver(diagram)
```

#### Key Features of ERD

**1. Business Semantics First**

```python
# ERD expresses business concepts, not database constraints
class TeamEntity(BaseModel, BaseEntity):
    __relationships__ = [
        # Team has multiple Sprints (business relationship)
        Relationship(field='id', target_kls=list[SprintEntity], loader=...),
        # Team has multiple members (business relationship, possibly via intermediate table)
        Relationship(field='id', target_kls=list[UserEntity], loader=...),
        # Team has multiple tasks (business relationship, possibly indirectly via Sprint)
        Relationship(field='id', target_kls=list[TaskEntity], loader=...),
    ]
```

This definition approach demonstrates ERD's core advantage. Starting from entity and relationship definitions, relationship-related data doesn't need to be pre-defined as field names in the entity. Entities only need to define core attributes of business concepts (like id, name), while associations are declared separately through `__relationships__`. This definition approach is closer to storage models, completely decoupling data structure definition from data fetching methods.

More importantly, this design provides an excellent foundation for composing response data structures through inheritance and extension. When different APIs need to return different data, you only need to inherit from the Entity and select the needed relationships, without pre-defining all possible fields in the Entity. This flexibility allows the same Entity to adapt to various business scenarios, truly achieving "define once, reuse everywhere."

**2. Multiple Relationships for the Same Field**

When the same field needs to establish multiple relationships to the same target type, use `MultipleRelationship`:

```python
from pydantic_resolve import MultipleRelationship, Link

class UserEntity(BaseModel, BaseEntity):
    """User entity - a user can relate to tasks in multiple ways"""
    __relationships__ = [
        # same field 'id', multiple business relationships to same target type
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

# use LoadBy in Response to distinguish different relationships
class UserWithCreatedTasksResponse(BaseModel):
    id: int
    name: str

    # use biz_name parameter to specify which relationship to load
    created_tasks: Annotated[list[TaskResponse], LoadBy('id', biz='created')] = []

class UserWithAssignedTasksResponse(BaseModel):
    id: int
    name: str

    assigned_tasks: Annotated[list[TaskResponse], LoadBy('id', biz='assigned')] = []
```

This feature is hard to implement in traditional SQLAlchemy ORM. In ORM, if User and Task have multiple association relationships (creation, assignment, review), you usually need to define multiple `relationship` attributes, but these attributes must be pre-defined in the Model class, and their business semantics cannot be clearly distinguished. Worse, ORM's relationship definitions are constrained by database foreign keys—if there's no corresponding database table structure, these relationships cannot be expressed.

But MultipleRelationship is different. It gives each relationship clear business meaning through the `biz` parameter. These business meanings are directly reflected in code, making relationships themselves carriers of business knowledge. `created`, `assigned`, `reviewed` are not just technical identifiers, but direct expressions of business domain. This design better matches real business scenarios, because a user's relationship with tasks can indeed have multiple business meanings, and ERD lets these business relationships be explicitly declared and clearly distinguished.

**3. Virtual Relationships (Database-Agnostic Business Relationships)**

Pydantic-resolve ERD's power lies in: **business relationships are not limited to database foreign keys**. Associated data can be loaded from any data source, including RPC services, local files, external APIs, etc.

```python
from pydantic_resolve import base_entity, Relationship

BaseEntity = base_entity()

# example 1: load user avatar from external RPC service
class UserEntity(BaseModel, BaseEntity):
    """User entity"""
    __relationships__ = [
        # relationship 1: tasks loaded from database (standard relationship)
        Relationship(
            field='id',
            target_kls=list[TaskEntity],
            loader=user_to_tasks_loader  # load from database
        ),
        # relationship 2: config loaded from file system (virtual relationship)
        Relationship(
            field='id',
            target_kls=UserConfigEntity,
            loader=user_config_from_file_loader  # load from JSON/YAML file
        ),
        # relationship 3: user profile loaded from RPC service (virtual relationship)
        Relationship(
            field='id',
            target_kls=UserProfileEntity,
            loader=user_profile_from_rpc_loader  # load from gRPC/HTTP RPC service
        ),
    ]
    id: int
    name: str
    email: str

class UserConfigEntity(BaseModel):
    """User config - from file system"""
    theme: str
    language: str
    notifications_enabled: bool

class UserProfileEntity(BaseModel):
    """User profile - from external service"""
    interests: list[str]
    skills: list[str]
    reputation_score: float

# loader implementation: load config from file system
async def user_config_from_file_loader(user_ids: list[int]) -> list[UserConfigEntity]:
    """load user config from local JSON file"""
    configs = []
    for user_id in user_ids:
        # read config file from file system
        config_path = f"/data/users/{user_id}/config.json"
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                configs.append(UserConfigEntity(**config_data))
        except FileNotFoundError:
            # config file doesn't exist, return default config
            configs.append(UserConfigEntity(
                theme='light',
                language='en',
                notifications_enabled=True
            ))
    return configs

# loader implementation: load user profile from RPC service
async def user_profile_from_rpc_loader(user_ids: list[int]) -> list[UserProfileEntity]:
    """load user profile from external gRPC service"""
    # batch call external RPC service
    async with UserProfileServiceClient() as client:
        # assume RPC service supports batch query
        request = GetBatchUserProfilesRequest(user_ids=user_ids)
        response = await client.get_batch_profiles(request)

        # convert to entities
        profiles = [
            UserProfileEntity(
                interests=p.interests,
                skills=p.skills,
                reputation_score=p.reputation_score
            )
            for p in response.profiles
        ]
        return profiles

# example 2: get real-time status from message queue
class OrderEntity(BaseModel, BaseEntity):
    """Order entity"""
    __relationships__ = [
        # query order history from database
        Relationship(
            field='id',
            target_kls=list[PaymentEntity],
            loader=order_to_payments_loader
        ),
        # get real-time status from Redis (cache/message queue)
        Relationship(
            field='id',
            target_kls=OrderStatusEntity,
            loader=order_status_from_redis_loader  # get real-time status from Redis
        ),
    ]
    id: int
    order_number: str

class OrderStatusEntity(BaseModel):
    """Order real-time status - from Redis"""
    status: str
    progress: int
    estimated_delivery: datetime
    last_updated: datetime

async def order_status_from_redis_loader(order_ids: list[int]) -> list[OrderStatusEntity]:
    """get order real-time status from Redis"""
    # batch read from Redis
    import redis.asyncio as redis

    redis_client = await redis.Redis(host='localhost', port=6379, db=0)
    statuses = []

    for order_id in order_ids:
        # read status from Redis Hash
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
            # no data in Redis, return default status
            statuses.append(OrderStatusEntity(
                status='pending',
                progress=0,
                estimated_delivery=None,
                last_updated=datetime.now()
            ))

    return statuses
```

This design brings significant advantages. First is data source independence—relationship definitions don't care where data comes from, whether it's database, file system, RPC service, message queue, or external API, and business logic remains consistent. Second, technical decoupling—when you need to switch data sources, you only modify the loader implementation; ERD definitions and business logic need no changes. Finally is performance optimization flexibility—you can choose the most appropriate storage for different data based on business needs: hot data in Redis, large file computation results in object storage, real-time status from message queue, truly letting "each specialty do its best."

### 3.3 DataLoader: The Secret of Batch Loading

#### Problem: N+1 Queries

```python
# traditional individual loading (N+1 problem)
tasks = [Task(1), Task(2), Task(3), ...]
for task in tasks:
    task.owner = await get_user(task.owner_id)  # N queries

# executed SQL:
# SELECT * FROM users WHERE id = 1
# SELECT * FROM users WHERE id = 2
# SELECT * FROM users WHERE id = 3
# ...
```

#### Solution: DataLoader

```python
from aiodataloader import DataLoader
from pydantic_resolve import build_list

class UserLoader(DataLoader):
    async def batch_load_fn(self, user_ids: list[int]):
        # 1. batch query (1 query)
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id.in_(user_ids))
            )
            users = result.scalars().all()

        # 2. build mapping: user_id -> User
        return build_list(users, user_ids, lambda u: u.id)

# usage
loader = UserLoader()
tasks = [Task(1), Task(2), Task(3), ...]
for task in tasks:
    task.owner = await loader.load(task.owner_id)  # auto batch

# executed SQL:
# SELECT * FROM users WHERE id IN (1, 2, 3, ...)  # only 1 query!
```

DataLoader's working principle is based on intelligent batching and caching mechanisms. When multiple load requests are initiated within the same event loop, they don't execute immediately but are first cached. For example, calling load(1), load(2), load(3) consecutively, these requests get temporarily cached. If load(1) is called again, due to cache hit it returns immediately. When the event loop reaches the right moment, all cached unique IDs get merged into one batch call batch_load_fn([1, 2, 3]), and query results are distributed to waiting requests.

This mechanism brings three key features. First is auto-batching: individual requests are automatically merged into batch requests without developers manually writing batch logic. Second is smart caching: the same ID is only queried once per resolution cycle, duplicate requests directly return cached results. Third is concurrent scheduling: leveraging Python's event loop mechanism to automatically coordinate batch timing, developers don't need to care about underlying scheduling details.

#### DefineSubset: Field Selection and Reuse

In actual development, different APIs often need to return different field combinations of the same entity. For example, one API only needs user basic info (id, name), another needs user detailed info (id, name, email), and yet another needs user statistics. If you define a complete Response Model for each API, it produces massive code duplication. `DefineSubset` provides an elegant way to reuse Entity definitions by selecting only needed fields.

**Basic Usage**

```python
from pydantic_resolve import DefineSubset

# Entity defines complete business entity
class UserEntity(BaseModel, BaseEntity):
    __relationships__ = [...]
    id: int
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime

# select needed fields through DefineSubset
class UserSummary(DefineSubset):
    __subset__ = (UserEntity, ('id', 'name', 'email'))

# automatically generates equivalent:
# class UserSummary(BaseModel):
#     id: int
#     name: str
#     email: str
```

The benefits are obvious: first, field types automatically inherit from Entity, no repetitive definition needed; second, when Entity fields change, all Response Models based on it automatically reflect those changes; finally, code is more concise, greatly reducing repetitive labor.

**Advanced Configuration: SubsetConfig**

If you need more complex configuration (like exposing fields to child nodes or sending to collectors), you can use `SubsetConfig`:

```python
from pydantic_resolve import DefineSubset, SubsetConfig

class StoryResponse(DefineSubset):
    __subset__ = SubsetConfig(
        kls=StoryEntity,                       # source model
        fields=['id', 'name', 'owner_id'],     # fields to include
        expose_as=[('name', 'story_name')]     # expose to child nodes with alias
    )

# equivalent to:
# class StoryResponse(BaseModel):
#     id: int
#     name: Annotated[str, ExposeAs('story_name')]
#     owner_id: int
```

**Synergy with ERD**

`DefineSubset` works even better when combined with ERD. Entity defines all possible relationships through ERD, while Response Model selects current needed fields and relationships through `DefineSubset`. This separation completely decouples business definition from use case.

```python
# Entity definition: complete model of business entity
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

# API 1: only need task basic info
class TaskSummaryResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name'))

# API 2: need task and its owner
class TaskWithOwnerResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name', 'estimate', 'owner_id'))
    owner: Annotated[Optional[UserResponse], LoadBy('owner_id')] = None

# API 3: need task and its belonging Story
class TaskWithStoryResponse(DefineSubset):
    __subset__ = (TaskEntity, ('id', 'name', 'story_id'))
    story: Annotated[Optional[StoryResponse], LoadBy('story_id')] = None
```

**Core Philosophy**

`DefineSubset` embodies the design philosophy of "define once, reuse everywhere." Entity is the complete definition of business concepts, the "single source of truth"; Response Model is field selection for specific use cases, an "adapter for usage scenarios." This separation ensures consistency of business definitions while retaining enough flexibility to adapt to various API needs.

### 3.4 Resolve and Post: Data Assembly and Computation

#### Resolve: Declaring Data Dependencies

```python
class TaskResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    # resolve: load through DataLoader
    owner: Optional[UserResponse] = None
    def resolve_owner(self, loader=Loader(user_batch_loader)):
        return loader.load(self.owner_id)
```

Resolver's workflow consists of four steps. First, scan all `resolve_{field}` methods in Response Model, identifying fields that need resolution. Then collect all IDs that need loading—for example, 100 Task objects might produce 50 different owner_ids. Next, batch call the corresponding loader to fetch all needed User data in one query. Finally, fill query results into corresponding fields according to ID mapping. The entire process is fully automated.

#### Post: Data Post-processing

```python
class StoryResponse(BaseModel):
    id: int
    name: str

    tasks: list[TaskResponse] = []
    def resolve_tasks(self, loader=Loader(story_to_tasks_loader)):
        return loader.load(self.id)

    # post: calculate after tasks loading completes
    total_estimate: int = 0
    def post_total_estimate(self):
        return sum(t.estimate for t in self.tasks)

    completed_count: int = 0
    def post_completed_count(self):
        return sum(1 for t in self.tasks if t.status == 'done')
```

Execution order is carefully designed to ensure data dependency correctness. First execute all resolve methods—these can run in parallel since they have no dependencies. Then wait for all async operations to complete, ensuring all associated data is loaded. Finally execute all post methods—these run serially because they might need to access data loaded by resolve methods, or perform cross-field data computation. This two-phase design guarantees that when computing derived fields, all base data is ready.

### 3.5 Cross-Layer Data Transfer

#### Expose: Parent Exposes Data to Children

```python
from pydantic_resolve import ExposeAs

class StoryResponse(BaseModel):
    id: int
    name: Annotated[str, ExposeAs('story_name')]  # expose to child nodes

    tasks: list[TaskResponse] = []

class TaskResponse(BaseModel):
    id: int
    name: str

    # post methods can access data exposed by ancestor nodes
    full_name: str = ""
    def post_full_name(self, ancestor_context):
        story_name = ancestor_context.get('story_name')
        return f"{story_name} - {self.name}"
```

**Data flow**:
```
Story (story_name: "Sprint 1")
  └─ Task (name: "Fix bug")
      └─ full_name: "Sprint 1 - Fix bug"
```

#### Collect: Parent Collects Data from Children

```python
from pydantic_resolve import Collector, SendTo

class TaskResponse(BaseModel):
    id: int
    owner_id: int

    # load owner, send to parent's collector
    owner: Annotated[
        Optional[UserResponse],
        LoadBy('owner_id'),
        SendTo('related_users')  # send to collector
    ] = None

class StoryResponse(BaseModel):
    id: int
    name: str

    tasks: list[TaskResponse] = []

    # collect all child nodes' owners
    related_users: list[UserResponse] = []
    def post_related_users(self, collector=Collector(alias='related_users')):
        return collector.values()
```

**Data flow**:
```
Story
  ├─ Task 1 (owner: Alice)
  ├─ Task 2 (owner: Bob)
  └─ Task 3 (owner: Alice)  ← deduplicated

Story.related_users: [Alice, Bob]
```

### 3.6 Summary

Pydantic-Resolve abstracts common patterns in building business data at appropriate granularity through multiple dimensions, forming a simple yet powerful toolkit.

**Core abstraction dimensions**:

1. **ERD (Entity Relationship Diagram)**: completely decouples business relationship definition from data fetching, declaratively describing relationships between entities
2. **DataLoader**: auto batch loading, avoids N+1 query problems, makes performance optimization transparent
3. **DefineSubset**: select field combinations from Entity, achieves "define once, reuse everywhere," avoids code duplication
4. **Resolve/Post**: separates data loading from computation, keeps each method's responsibility single
5. **Expose/Collect**: provides cross-layer data transfer capability, supports parent exposing data to children and children collecting data from parent
6. **LoadBy**: auto-resolve relationships based on ERD, reduces code duplication

These abstraction dimensions remain orthogonal, each solving a specific problem, without interfering yet freely composable. DefineSubset handles field selection, ERD defines relationships, LoadBy uses relationships, DataLoader handles batch loading, Resolve/Post handles data assembly and computation, Expose/Collect handles cross-layer data transfer. Each does its job well.

---

## 4. FastAPI-Voyager: Architecture Visualization

### 4.0 Why Architecture Visualization?

If you've used GraphQL, you're surely impressed by GraphiQL. GraphiQL is an interactive IDE that lets you:
- Browse complete GraphQL Schema
- Explore each Type's fields and relationships
- Write and test queries in real-time
- View query result type information

GraphiQL's core value lies in: **it makes invisible Schema visible and explorable**. Developers no longer need to read extensive documentation or code to quickly understand GraphQL API structure.

But in RESTful API + Pydantic-Resolve architecture, we face similar challenges. Although we have ERD to define business entity relationships, and Response Models to define API return structures, this information is scattered across various places in the code. Without tool support, developers need to:
- Read extensive code to understand business relationships
- Manually trace data flow
- Struggle to discover architecture drift or excessive nesting

**FastAPI-Voyager is like GraphiQL for the Pydantic-Resolve world**.

It provides similar interactive exploration experience, but oriented towards RESTful API architecture:
- **Visualized ERD**: see all entities and their relationships
- **API dependency graph**: view each API's returned data structure and dependencies
- **Interactive exploration**: click any node to view upstream and downstream dependencies
- **Real-time updates**: view refreshes automatically as code changes

But more importantly, Voyager provides unique advantages that GraphiQL doesn't have:

| Dimension | GraphiQL (GraphQL) | FastAPI-Voyager (Pydantic-Resolve) |
|------|-------------------|----------------------------------|
| **Business model** | Schema mixes entities and use cases | ERD independently defines business entities |
| **Use case boundaries** | blurred, hard to distinguish | clear, each Route is a use case |
| **Relationship definitions** | hidden in Schema | explicitly declared in ERD |
| **Data flow** | need to read Resolver | visualized dependency chains |
| **Performance insights** | hard to discover N+1 | color-marked resolve/post operations |

GraphiQL makes GraphQL Schema visible, while Voyager makes the separation between business models and use cases visible. It not only displays API structure, but more importantly shows **how business models are used by different use cases**, which is the core idea of Clean Architecture.

### 4.1 Core Features

FastAPI-Voyager is a tool that visualizes FastAPI application architecture. It can:

#### 1. Automatic API Structure Scanning

```python
from fastapi import FastAPI
from fastapi_voyager import create_voyager

app = FastAPI()

# automatically scan all routes
voyager_app = create_voyager(
    app,
    enable_pydantic_resolve_meta=True  # show pydantic-resolve metadata
)

app.mount("/voyager", voyager_app)
```

Visit `http://localhost:8000/voyager` to view visualization.

**Live Demo**: experience [FastAPI-Voyager Live Demo](https://www.newsyeah.fun/voyager/?tag=demo) to see architecture visualization in a real project.

#### 2. Three-Layer Architecture Display

```
┌────────────────────────────────────┐
│  Tag Layer (use case grouping)       │
│  ┌────────┐  ┌────────┐  ┌────────┐│
│  | users  |  | teams  |  | tasks  ││
│  └────┬───┘  └────┬───┘  └────┬───┘│
└───────┼────────────┼────────────┼───┘
        │            │            │
        ↓            ↓            ↓
┌────────────────────────────────────┐
│  Route Layer (interface layer)      │
│  ┌────────────┐  ┌────────────┐   │
│  | GET /users |  | POST /teams|   │
│  └──────┬─────┘  └──────┬─────┘   │
└─────────┼────────────────┼─────────┘
          │                │
          ↓                ↓
┌────────────────────────────────────┐
│  Schema Layer (business model layer)│
│  ┌──────┐  ┌──────┐  ┌──────┐    │
│  | User |←─| Team |→─| Task |    │
│  └──────┘  └──────┘  └──────┘    │
└────────────────────────────────────┘
```

Pydantic-resolve operations are marked with different colors for intuitive display:

- **resolve** (green): data loaded through DataLoader
- **post** (blue): fields computed after all resolve completes
- **expose as** (purple): fields exposed to descendant nodes
- **send to** (red): fields sent to parent node's collector
- **collectors** (black): fields collected from child nodes

### 4.2 Combining ERD with API Routes

#### Core: Business-Technical Mapping

```python
# 1. define ERD
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

# 2. integrate with Voyager
voyager_app = create_voyager(
    app,
    er_diagram=diagram,  # ← ERD combined with API
    enable_pydantic_resolve_meta=True
)
```

**Visualization effect**:

```
API Route (GET /users/{user_id})
    ↓ returns
UserResponse
    ├─ owner: LoadBy('owner_id') ────→ UserEntity (green)
    ├─ tasks: LoadBy('id') ──────────→ list[TaskEntity] (green)
    │   └─ owner: LoadBy('owner_id') ─→ UserEntity (green)
    └─ total_tasks: post_total_tasks() (blue)

ERD displayed entity relationships:
UserEntity ──────────→ TaskEntity
   │                     │
   └─────────────────────┘
```

### 4.3 Practical Application Scenarios

#### Scenario 1: Discovering Architecture Drift

In actual development, API implementation easily drifts from the designed business model. For example, ERD only defines User → Task relationship, but some API's Response Model contains Profile field. In Voyager, this becomes obvious: click `get_user` route, see it returns `UserWithProfileResponse`, ERD diagram shows no `User → Profile` link. **Problem discovered**: API implementation deviates from business model.

#### Scenario 2: Discovering Excessive Nesting

Excessive nesting is a common issue affecting API performance and maintainability. When one API returns Team → Sprints → Stories → Tasks → Owner with five levels of nesting, query complexity grows sharply. In Voyager, click `get_team` route and see a long dependency chain. The chain's length directly reflects nesting depth. **Problem discovered**: should split API or use field selection.

#### Scenario 3: Quick Onboarding for New Team Members

Traditional approach: read hundreds of pages of documentation, check scattered code, ask experienced employees.

Using Voyager: open /voyager, click the API of interest, see dependent models and relationships. Understand core business workflows in 5 minutes. This visualization significantly reduces the cost of team knowledge transfer.

---

## 5. Complete Development Workflow

### 5.1 Architecture Design Phase

#### Step 1: Identify Core Business Entities

```markdown
Problem domain: project management system

Core entities:
- User (user)
- Team (team)
- Sprint (sprint)
- Story (story)
- Task (task)
```

#### Step 2: Define Entity Relationships

```markdown
Business relationships:
- Team 1:N User (team members)
- Team 1:N Sprint (sprints)
- Sprint 1:N Story (stories)
- Story 1:N Task (tasks)
- Task N:1 User (task owner)
```

### 5.2 Entity Definition Phase

#### Define ERD

```python
from pydantic_resolve import base_entity, Relationship, config_global_resolver

BaseEntity = base_entity()

class UserEntity(BaseModel, BaseEntity):
    """User entity"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[TaskEntity], loader=user_to_tasks_loader),
        Relationship(field='id', target_kls=list[TeamEntity], loader=user_to_teams_loader),
    ]
    id: int
    name: str
    email: str

class TeamEntity(BaseModel, BaseEntity):
    """Team entity"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[SprintEntity], loader=team_to_sprints_loader),
        Relationship(field='id', target_kls=list[UserEntity], loader=team_to_users_loader),
    ]
    id: int
    name: str

class SprintEntity(BaseModel, BaseEntity):
    """Sprint entity"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[StoryEntity], loader=sprint_to_stories_loader),
    ]
    id: int
    name: str
    team_id: int

class StoryEntity(BaseModel, BaseEntity):
    """Story entity"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[TaskEntity], loader=story_to_tasks_loader),
    ]
    id: int
    name: str
    sprint_id: int

class TaskEntity(BaseModel, BaseEntity):
    """Task entity"""
    __relationships__ = [
        Relationship(field='owner_id', target_kls=UserEntity, loader=user_loader),
    ]
    id: int
    name: str
    owner_id: int
    story_id: int
    estimate: int

# register ERD
diagram = BaseEntity.get_diagram()
config_global_resolver(diagram)
```

### 5.3 Data Layer Implementation

#### Define ORM Models (guided by ERD)

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
    """intermediate table: many-to-many relationship"""
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

#### Implement Loaders

```python
from aiodataloader import DataLoader
from pydantic_resolve import build_list

async def user_loader(user_ids: list[int]):
    """load users"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = result.scalars().all()
        return build_list(users, user_ids, lambda u: u.id)

async def team_to_sprints_loader(team_ids: list[int]):
    """load team's Sprints"""
    async with get_session() as session:
        result = await session.execute(
            select(Sprint).where(Sprint.team_id.in_(team_ids))
        )
        sprints = result.scalars().all()
        return build_list(sprints, team_ids, lambda s: s.team_id)

async def team_to_users_loader(team_ids: list[int]):
    """load team members (via intermediate table)"""
    async with get_session() as session:
        result = await session.execute(
            select(User)
            .join(TeamMember, TeamMember.user_id == User.id)
            .where(TeamMember.team_id.in_(team_ids))
        )
        users = result.scalars().all()

        # build mapping: team_id -> list[User]
        users_by_team = {tid: [] for tid in team_ids}
        for user in users:
            for tm in user.team_memberships:
                if tm.team_id in users_by_team:
                    users_by_team[tm.team_id].append(user)

        return [users_by_team.get(tid, []) for tid in team_ids]
```

### 5.4 API Implementation Phase

#### Define Response Models

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

    # calculate total estimate
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

    # calculate total tasks
    total_tasks: int = 0
    def post_total_tasks(self):
        count = 0
        for sprint in self.sprints:
            for story in sprint.stories:
                count += len(story.tasks)
        return count
```

#### Implement API Routes

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/teams", tags=['teams'])

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    session: AsyncSession = Depends(get_session)
):
    # 1. get base data from database
    team = await session.get(Team, team_id)
    await session.close()

    # 2. convert to Response Model
    team_response = TeamResponse.model_validate(team)

    # 3. resolve all associated data
    result = await Resolver().resolve(team_response)

    return result
```

### 5.5 Visualization Verification

#### Integrate FastAPI-Voyager

```python
from fastapi import FastAPI
from fastapi_voyager import create_voyager

app = FastAPI()

# mount Voyager
app.mount('/voyager', create_voyager(
    app,
    er_diagram=diagram,  # pass ERD
    enable_pydantic_resolve_meta=True
))

# register routes
app.include_router(router)
```

#### Verify Architecture

1. Visit `http://localhost:8000/voyager`
2. Check ERD: confirm entity relationships display correctly
3. Click API: view data flow
4. Discover problems:
   - Are there circular dependencies?
   - Is there excessive nesting?
   - Are there missing relationships?

---

## 6. Comparison with Other Approaches

### 6.1 vs Traditional ORM

| Dimension | Traditional ORM (SQLAlchemy) | Pydantic-Resolve |
|------|----------------------|------------------|
| **Focus** | Data persistence | Business data assembly |
| **Relationship definition** | Based on foreign key constraints | Based on business semantics |
| **Data loading** | Eager/Lazy Loading | DataLoader batch loading |
| **Flexibility** | Limited by database structure | Fully flexible |
| **N+1 problem** | Prone to occur, requires manual optimization | Auto-avoided |
| **Business expression** | Hidden in queries | Explicitly declared |
| **Testing** | Depends on database | Can test independently |

### 6.2 vs GraphQL

| Dimension | GraphQL | Pydantic-Resolve |
|------|---------|------------------|
| **Query method** | Frontend custom queries | Backend defines Schema |
| **Type safety** | Needs SDL + toolchain | Native Pydantic |
| **Learning curve** | Steep | Gentle |
| **Performance** | DataLoader (manual config) | DataLoader (auto) |
| **Debugging** | Complex | Simple (Python code) |
| **Integration** | Needs additional server | Native FastAPI |
| **Flexibility** | Overly flexible, hard to optimize | Clear API contracts |
| **ERD/use case separation** | Blurred, mixed in Schema | Clear separation, ERD independent |

### 6.3 vs DDD Frameworks

| Dimension | DDD Frameworks (e.g., Django-eav) | Pydantic-Resolve |
|------|------------------------|------------------|
| **Complexity** | High (complete DDD implementation) | Low (only focus on data assembly) |
| **Domain model** | Forces DDD concepts | Flexible, optional use |
| **Relationship with ORM** | Encapsulates ORM | Works with ORM |
| **Learning cost** | High | Low |
| **Applicable scenarios** | Large complex domains | Small to medium projects |

---

## 7. Conclusion

### Core Values

The development method based on Pydantic-Resolve and FastAPI-Voyager achieves the following core values:

#### 1. Business Model First

```python
# ERD = direct expression of business language
class TeamEntity(BaseModel, BaseEntity):
    """Team - business concept"""
    __relationships__ = [
        Relationship(field='id', target_kls=list[SprintEntity], loader=...),
    ]
```

This approach makes business relationships explicitly declared, all entity relationships clearly defined in ERD, no longer hidden in code or SQL statements. More importantly, business modeling is completely free from database structure limitations, can express cross-database, cross-service business relationships, even supports virtual relationships loading from non-database sources like RPC, file systems. Truly achieves decoupling of business concepts from technical implementation.

#### 2. Clean Architecture Implementation

Dependency direction from outer to inner layers is clear and explicit: FastAPI Routes → Response Models → Entity + ERD → Loaders → ORM. This fully complies with Clean Architecture's dependency rules. Outer layers depend on inner layers, inner layers are completely independent of outer layers, business rules don't depend on any framework or technical implementation. When needing to switch databases, ORM frameworks or Web frameworks, core business logic needs no modifications.

#### 3. Automatic Performance Optimization

```python
# DataLoader auto batch loading
tasks = [Task(1, owner_id=1), Task(2, owner_id=2), ...]
result = await Resolver().resolve(tasks)

# auto merged into one query:
# SELECT * FROM users WHERE id IN (1, 2, ...)
```

DataLoader's auto batch loading mechanism makes performance optimization transparent. Developers don't need to worry about N+1 query problems, all associated data loading gets automatically merged into batch queries. Query optimization is transparent, developers only need to declare data dependencies, framework automatically selects optimal query strategy. This "high performance by default" design lets developers focus on business logic without worrying about performance traps.

#### 4. Architecture Visualization

```python
# FastAPI-Voyager visualizes architecture
app.mount('/voyager', create_voyager(
    app,
    er_diagram=diagram,
    enable_pydantic_resolve_meta=True
))
```

FastAPI-Voyager presents architecture in a visualized manner, providing a mapping of business models to technical implementation. Developers can intuitively see each API's returned data structure, dependencies, and data flow. The view updates in real-time as code changes, always staying in sync. More importantly, it provides interactive exploration capability—click any node to view its dependencies and dependents, making architecture understanding unprecedentedly simple.

#### 5. Development Efficiency Improvement

| Phase | Traditional approach | Using this toolkit |
|------|---------|-------------|
| Design phase | Text description, easy to miss | ERD visualization, clear expression |
| Development phase | Manual data assembly, duplicate code | Declarative, auto resolution |
| Testing phase | Needs database | Business logic testable independently |
| Debugging phase | Read code, hard to understand | Graphically view dependency relationships |
| Maintenance phase | Modify multiple places, error-prone | Centralized management, impact analysis |

#### 6. Easier Testing and Debugging

```python
# DataLoader: single responsibility, easy to test
async def user_loader(user_ids: list[int]):
    """batch load users - only does one thing, maps IDs to users"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = result.scalars().all()
        return build_list(users, user_ids, lambda u: u.id)

# testing is very simple: just mock the loader
async def test_task_response():
    # no database needed
    mock_users = [User(id=1, name="Alice")]
    with patch('user_loader', return_value=mock_users):
        result = await Resolver().resolve(tasks)
        assert result[0].owner.name == "Alice"
```

DataLoader's query logic is much simpler compared to nested SQL in traditional approaches. Each loader only handles one simple batch query: return corresponding data based on ID list. This single-responsibility design makes loaders very easy to test, only need to mock input and output, without starting complete database environment.

More importantly, when debugging it's easy to isolate problems. When an API's data loading has issues, you can quickly locate which loader errored through Voyager, then test that loader in isolation. This "small and focused" function design makes debugging unprecedentedly simple. Compared to traditional approaches with hundreds of lines of complex SQL or nested data assembly logic, a single loader is usually only a dozen lines, making problem troubleshooting and fixes more efficient.

### Applicable Scenarios

#### Recommended Use Cases

This method is best suited for complex business scenarios, where the system has multi-level nested relationships, needs cross-entity data aggregation, or has complex business rules. Its advantages are very obvious. For team collaboration scenarios, especially when clear architecture documentation is needed, new members join frequently, or strict code review is required, visualized architecture diagrams can significantly improve communication efficiency. Long-term maintenance projects also benefit—during continuous business logic evolution, ERD helps maintain architecture clarity, preventing technical debt accumulation. For performance-sensitive applications that need to avoid N+1 queries, need batch loading optimization, or need flexible query strategies, DataLoader's auto-batch mechanism brings significant performance improvements.

#### Not Recommended Use Cases

Of course, this method is not suitable for all scenarios. For simple CRUD applications, if there are only single-table operations and no complex associations, using this method might be over-designed, instead adding unnecessary complexity. For scenarios with extremely high real-time requirements, DataLoader's batch mechanism brings slight latency (though usually at the millisecond level), which might be inappropriate for certain ultra-low latency requirements (like high-frequency trading). In these cases, directly handwritten optimized queries might have better performance.

### Closing Remarks

Pydantic-Resolve and FastAPI-Voyager combination provides a **business-model-centric** architecture method for Python web development. It's not meant to replace existing tools (like SQLAlchemy, FastAPI), but to **supplement** their shortcomings in business modeling and data assembly.

The core idea of this method is:

> **"Let code reflect business, not make business adapt to code"**

More deeply, the core idea of this approach is **respecting business complexity** while minimizing related code complexity on that foundation. Business itself is complex—various entity relationships, business rules, use case scenarios—these complexities are unavoidable. But code complexity can be reduced through abstraction and encapsulation.

Pydantic-Resolve encapsulates common code patterns into several clear concepts through DSL-like approaches:
- **ERD** encapsulates business relationship declarations
- **DataLoader** encapsulates batch loading logic
- **Resolve/Post** encapsulates data assembly and computation flow
- **Expose/Collect** encapsulates cross-layer data transfer patterns
- **LoadBy** encapsulates relationship reuse logic

These concepts are like a DSL specific to data assembly domain, letting developers describe "what they want" in a declarative way rather than writing "how to fetch" in imperative style. Code noise that's scattered across various places—batch query loops, dictionary mapping construction, nested data assembly, cache management—all get encapsulated into these concepts, thereby significantly reducing overall code complexity.

When reading code written with Pydantic-Resolve, developers see clear business intent rather than technical details of data manipulation. This noise reduction effect makes code easier to understand, maintain, and evolve.

Through ERD explicitly declaring business relationships, through Resolver automatically assembling data, through Voyager visualizing architecture, we can build clearer, more maintainable, higher-performance web applications.

On the journey of software architecture, there's no silver bullet. But this method at least provides us with a **feasible path to practicing Clean Architecture in reality**.

---

## References

- [Pydantic-Resolve Documentation](https://allmonday.github.io/pydantic-resolve/)
- [FastAPI-Voyager Repository](https://github.com/allmonday/fastapi-voyager)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [DataLoader (Facebook)](https://github.com/facebook/dataloader)

---

**Document Version**: 1.0
**Last Updated**: 2025-01-11
**Author**: tangkikodo
EOFRAGMENT
