# LLM-Filter 智能对话过滤系统

[![License: MIT](https://img.shields.io/badge/License-MIT-blue)](LICENSE) [![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](docker-compose.yml) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-4169E1?logo=postgresql&logoColor=white)](scripts/init_postgres.sql) [![MongoDB](https://img.shields.io/badge/MongoDB-6%2B-47A248?logo=mongodb&logoColor=white)](scripts/init_mongo.py) [![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000)](https://ollama.com/) [![Dify](https://img.shields.io/badge/Dify-Agent-5B2EFF)](https://dify.ai/) [![Go](https://img.shields.io/badge/Go-1.x-00ADD8?logo=go&logoColor=white)](microservices/auth-service/go.mod) [![Spring Boot](https://img.shields.io/badge/Spring%20Boot-2%2B-6DB33F?logo=springboot&logoColor=white)](microservices/edu-service/pom.xml) [![FastAPI](https://img.shields.io/badge/FastAPI-0.1xx-009688?logo=fastapi&logoColor=white)](microservices/llm-service/app/main.py)

一个面向教育与企业双场景的智能对话过滤系统，基于 **微服务架构** 重构，集成了高效敏感词过滤、严格的角色与版别控制、以及完善的教务/企业数据管理。

系统采用 **Go (认证)** + **Java (教务)** + **Python (LLM)** 的混合技术栈，充分发挥各语言优势，通过 **Docker Compose** 统一编排部署。

## 快速开始（只使用 `start.sh`）

```bash
# 1) 首次生成 .env
./start.sh init-env

# 2) 启动全部服务并初始化演示数据
./start.sh up --init-data

# 3) 查看状态与日志
./start.sh ps
./start.sh logs
```

`.env` 使用说明：
1. `./start.sh init-env` 会自动生成根目录 `.env`。
2. 启动时 `./start.sh up` 会把 `.env` 注入所有容器。
3. 首次启动如需默认账号/教务示例/敏感词，请执行 `./start.sh init-data`（或直接 `./start.sh up --init-data`）。
4. Dify 建议分别填写 `DIFY_API_KEY_LLM`（LLM 服务）与 `DIFY_API_KEY_SECURITY`（Security 服务）；旧版 `DIFY_API_KEY` 仍兼容。
5. 修改 `.env` 后可重构容器生效：`./start.sh rebuild`（或全量重启：`./start.sh down && ./start.sh up`）。
6. 如果 `.env` 权限异常，可执行：`sudo chown $USER:staff .env && chmod 640 .env`。

常用维护命令：
- `./start.sh rebuild [service]`：重构容器（默认全部，可指定服务）
- `./start.sh rm <service...>`：删除指定容器（可多个）
- `./start.sh init-data [--yes]`：初始化演示数据（会重置业务数据）

## 系统架构

本项目包含以下核心服务，通过 **Gateway (Nginx)** 统一对外暴露：

| 服务名称 | 技术栈 | 端口 (内部) | 职责描述 |
| :--- | :--- | :--- | :--- |
| **Gateway** | Nginx | 8080 | 统一 API 网关，负责请求路由转发与跨域处理 |
| **Auth Service** | Go (Gin) | 8081 | 用户注册、登录、JWT 签发、绑定管理 |
| **Edu Service** | Java (Spring Boot) | 8082 | 教务/业务核心服务（班级、人员、教师、课表、看板等） |
| **Security Service** | Python (FastAPI) | 8003 | 安全分析、风险监测、攻击应急、安全日报 |
| **LLM Service** | Python (FastAPI) | 8000 | 智能对话、敏感词过滤、审计日志、敏感词管理 |

### 基础设施
- **PostgreSQL**: 存储用户账户、角色信息及教务核心结构化数据。
- **MongoDB**: 存储非结构化数据，如对话历史、敏感词库、审计日志、部分教务冗余数据。
- **Ollama**: 本地大模型推理引擎（需单独部署或配置）。

## 功能概览

- **微服务设计**: 各模块职责单一，支持独立部署与扩展，降低耦合。
- **多语言融合**: 
  - **Go**: 高性能处理高频的认证与鉴权请求。
  - **Java**: 成熟生态支撑复杂的教务业务逻辑与事务。
  - **Python**: 灵活处理 AI 对话逻辑与数据分析。
- **智能对话**: 集成 Ollama，支持多种本地模型，低成本私有化部署。
- **安全过滤**: 内置高效 Trie 树敏感词过滤，支持实时热更新，保障合规。
- **角色权限**: 精细化的 RBAC 权限控制（学生/教师/管理员等）及版别控制（教育版/企业版）。

## 模块详解

### Gateway（Nginx）

- **统一入口**：对外只暴露一个入口，由网关按路径将请求转发到各后端服务。
- **接口文档**：统一管理所有微服务的 Swagger 文档入口
  - **LLM Service**: `http://localhost:8080/docs/llm`
  - **Security Service**: `http://localhost:8080/docs/security`
  - **Edu Service**: `http://localhost:8080/docs/edu`
  - **Auth Service**: `http://localhost:8080/docs/auth`
- **路由转发**：
  - 认证服务：`/api/v1/auth/*`、`/api/v1/bindings/*`
  - 教务服务：`/api/v1/classes/*`、`/api/v1/persons/*`、`/api/v1/teachers/*`、`/api/v1/schedules/*`、`/api/v1/dashboard/*`、`/api/v1/edu/*`
  - 安全服务：`/api/v1/security/*`
  - LLM 服务：其余路径默认转发（包含 `/docs`、`/api/v1/*` 等）
- **跨域与压缩**：统一设置 CORS 响应头与 gzip，减少前端对接成本。

### Auth Service（Go / Gin）

- **注册登录**：
  - `POST /api/v1/auth/register`：注册用户（默认 `role=user`，`edition=edu`）
  - `POST /api/v1/auth/login`：登录并签发 JWT，响应包含 `token` 与 `user`
- **账号与安全**：
  - 密码使用 bcrypt 加密存储
  - JWT 使用 HS256 对称签名（由 `JWT_SECRET` 控制密钥）
- **身份绑定（Binding）**：用于将“账号”绑定到具体业务身份（如学生/教师）：
  - `POST /api/v1/bindings`：创建绑定
  - `GET /api/v1/bindings/me`：获取当前用户主绑定
  - `DELETE /api/v1/bindings/{person_id}`：解绑
- **JWT 载荷（Claims）**：服务在签发 Token 时会携带下列字段，供下游服务直接做本地鉴权：
  - `sub`（用户ID）、`name`（用户名）、`role`、`role_level`、`edition`、`person_id`、`person_type`

### Edu Service（Java / Spring Boot）

- **基础数据管理**：
  - 班级与班主任：`GET /api/v1/classes`、`PUT /api/v1/classes/{classId}/head-teacher`
  - 人员信息：`POST /api/v1/persons/bulk`、`GET /api/v1/persons`
  - 教师信息：`POST /api/v1/teachers/bulk`、`GET /api/v1/teachers`
  - 课表与任课教师：`GET /api/v1/schedules`、`PUT /api/v1/schedules/assign-teacher`
- **看板能力（按角色输出不同视图）**：
  - 学生：`/api/v1/dashboard/student/today`、`/api/v1/dashboard/student/week`
  - 教师：`/api/v1/dashboard/teacher/week`
  - 班主任：`/api/v1/dashboard/homeroom/current`
  - 部门负责人：`/api/v1/dashboard/department/overview`
  - 校级管理：`/api/v1/dashboard/campus/overview`
- **JWT 本地解析**：通过 `JwtAuthenticationFilter` 解析 `Authorization: Bearer <token>`，将用户信息写入 `UserContext`，业务层可直接读取当前用户身份。

### Security Service（Python / FastAPI）

- **AI 安全分析**：
  - `POST /api/v1/security/analysis`：基于设备信息（交换机/防火墙/服务器）进行 AI 安全隐患分析
  - `POST /api/v1/security/attack/advice`：针对正在遭受的攻击提供 AI 应急建议
- **风险监测与日报**：
  - `GET /api/v1/security/monitor/risk`：AI 联网检索最新漏洞与合规风险
  - `GET /api/v1/security/reports/daily`：生成企业安全状态日报
- **权限控制**：仅限管理员（`role_level >= 9`）访问

### LLM Service（Python / FastAPI）

- **对话管理**：
  - `POST /api/v1/conversations`：创建会话
  - `GET /api/v1/conversations`：获取会话列表（列表场景仅返回最近一条消息以降低负载）
  - `GET /api/v1/conversations/{conversation_id}`：获取会话详情
  - `DELETE /api/v1/conversations/{conversation_id}`：删除会话
- **对话发送与过滤链路**：`POST /api/v1/conversations/{conversation_id}/messages`
  - 本地 Trie 过滤：使用内存 Trie 对用户输入做敏感词匹配
  - 智能体二次过滤（可选）：本地过滤通过后，可调用 Dify 智能体做内容安全复核
  - 审计留痕：命中敏感内容会写入 `sensitive_records`，并在会话消息中记录命中详情
  - 生成回复：未命中敏感内容时调用 Ollama 生成回复
- **敏感词与审计管理（管理员）**：
  - 敏感词：新增/删除/查询、批量导入（JSON/CSV）
  - 命中记录：按用户、会话、时间范围、分类、严重程度筛选
  - 分类管理：提供默认分类配置并支持扩展

## 角色等级与权限控制

系统使用“角色等级（role_level）”统一描述权限强弱，数字越大权限越高：

| 角色 | 等级 | 典型含义 |
| :--- | :---: | :--- |
| user | 1 | 学生/员工 |
| manager | 2 | 班主任/组长/二级部门管理员 |
| leader | 3 | 中层干部/部门负责人/一级部门管理员 |
| master | 4 | 校长/集团高管/业务最高负责人 |
| administrator / admin | 5 | 系统管理员/运维超管（系统最高） |

亮点与落地方式：

- **跨服务一致性**：Auth 在签发 JWT 时写入 `role`/`role_level`，下游服务本地解析后即可做鉴权，不依赖回源查询。
- **最小权限校验**：LLM 服务提供 `require_role(min_level)` 依赖工厂，用“最小等级”表达权限门槛，避免到处硬编码角色字符串。
- **管理员能力隔离**：LLM 管理类接口统一走管理员校验（兼容 `admin` 与 `administrator` 两种命名）。

## 版别控制（教育版 / 企业版）

- **版别字段**：用户与 Token 可携带 `edition`（`edu` 或 `biz`）。
- **运行模式开关**：LLM 服务通过 `APP_MODE` 限制接口仅允许对应版别用户访问（在路由层统一挂载依赖，减少遗漏风险）。

## 数据存储与审计

- **PostgreSQL（结构化）**：用户账号、角色/版别、教务核心实体（班级/人员/教师/课表等）。
- **MongoDB（非结构化）**：
  - `conversations`：对话会话与消息历史
  - `sensitive_words`：敏感词库（含分类、子类、严重程度）
  - `sensitive_records`：敏感命中审计记录（按用户/会话/时间/严重程度可检索）

## 文档
- 启动与本地开发：见 [DEVELOPMENT.md](file:///Users/uu/Desktop/dles_prj/llm-filter/DEVELOPMENT.md)
- 默认账号与初始化数据：见 [ACCOUNTS.md](file:///Users/uu/Desktop/dles_prj/llm-filter/ACCOUNTS.md)

## 许可证
MIT License
