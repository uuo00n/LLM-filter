# 微服务架构重构方案

## 1. 现状分析
当前项目是一个基于 Python FastAPI 的单体应用，主要包含以下业务领域：
- **认证与用户管理**：用户注册、登录、角色权限。
- **教育教务管理**：学生、教师、班级、课表、人员档案、绑定关系。
- **LLM 对话与过滤**：对话管理、敏感词过滤、对接 Ollama。
- **数据统计**：仪表盘。

**痛点（为什么感觉乱）：**
1.  **控制层与数据层耦合**：API 路由函数中直接包含大量 MongoDB 查询逻辑（如 `app/api/v1/auth.py`），缺乏独立的 Service 层封装。
2.  **业务边界模糊**：`bindings`（绑定关系）逻辑穿插在 Auth 和各个实体模块中。
3.  **单体膨胀风险**：教务逻辑（复杂的实体关系）与 AI 逻辑（无状态、流式、计算密集）混在一起，扩展性受限。

## 2. 拆分建议
建议将项目拆分为三个独立微服务，根据业务特性选择最适合的语言：

### 服务 A: 身份认证中心 (Identity Service)
-   **职责**：用户注册、登录、JWT 签发与验证、权限管理 (RBAC)、绑定关系管理。
-   **建议语言**：**Go** (Golang)
-   **数据库**：**PostgreSQL**
    -   **理由**：用户账户、角色权限是典型的结构化数据，关系型数据库能提供更好的事务支持和数据一致性保障。
-   **接管路由**：`/auth`, `/admin` (部分用户管理), `/bindings`

### 服务 B: 教务核心服务 (Edu Core Service)
-   **职责**：学生、教师、班级、课表、人员档案的 CRUD 与业务逻辑。
-   **建议语言**：**Java (Spring Boot)**
-   **数据库**：**PostgreSQL**
    -   **理由**：教务数据之间存在复杂的关联关系（如班级-学生、课程-教师），使用外键约束能有效维护数据完整性。Spring Data JPA 提供了强大的 ORM 支持。
-   **接管路由**：`/students`, `/teachers`, `/classes`, `/schedules`, `/persons`

### 服务 C: LLM 智能服务 (LLM Filter Service)
-   **职责**：LLM 对话管理、敏感词过滤算法、Ollama 接口对接。
-   **建议语言**：**Python** (保持现状)
-   **数据库**：**PostgreSQL (JSONB)** 或 **MongoDB**
    -   **理由**：对话记录虽然是非结构化的，但 PostgreSQL 的 JSONB 性能非常强劲，且便于与用户表做关联查询。为了简化运维，推荐全栈统一使用 PostgreSQL。
-   **接管路由**：`/conversations`, `/admin` (敏感词管理)

### 服务 D: 聚合层 / 网关 (API Gateway / BFF)
-   **职责**：统一入口，路由转发，或者聚合 Dashboard 数据。
-   **实现**：Nginx, Kong, 或一个轻量级的 Node.js/Go 服务。

## 3. 架构图示

```mermaid
graph TD
    Client[前端应用] --> Gateway[API 网关]
    
    Gateway -->|/auth, /bindings| AuthSvc[身份认证服务 (Go)]
    Gateway -->|/students, /classes| EduSvc[教务核心服务 (Go/Java)]
    Gateway -->|/conversations| LLMSvc[LLM 智能服务 (Python)]
    
    AuthSvc --> DB_PG[(PostgreSQL: AuthDB)]
    EduSvc --> DB_PG[(PostgreSQL: EduDB)]
    LLMSvc --> DB_PG[(PostgreSQL: LLMDB)]
    LLMSvc --> Ollama[Ollama LLM]
```

## 4. 迁移路线 (Strangler Fig Pattern)

1.  **第一步：提取公共依赖**
    -   确定服务间通信协议（推荐 RESTful HTTP 或 gRPC）。
    -   统一数据库设计（目前是共享 Mongo，微服务建议分库或分 Collection）。

2.  **第二步：剥离身份认证 (Auth Service)**
    -   优先用 Go 重写 `/auth` 模块。
    -   网关将 `/auth` 流量转发至新服务。
    -   Python 单体保留 JWT 验证逻辑（作为中间件），信任 Go 服务签发的 Token。

3.  **第三步：剥离教务业务**
    -   将 `/students` 等模块迁移至新服务。

4.  **第四步：瘦身 Python 服务**
    -   最后 Python 服务仅保留 LLM 相关核心业务，成为纯粹的 AI 服务。

## 5. 示例：用 Go 重构 Auth 服务

我们可以先尝试用 Go 重写 `register` 和 `login` 接口，展示微服务的结构。
