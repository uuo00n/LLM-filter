# LLM-Filter 智能对话过滤系统 (Microservices)

一个面向教育与企业双场景的智能对话过滤系统，基于 **微服务架构** 重构，集成了高效敏感词过滤、严格的角色与版别控制、以及完善的教务/企业数据管理。

系统采用 **Go (认证)** + **Java (教务)** + **Python (LLM)** 的混合技术栈，充分发挥各语言优势，通过 **Docker Compose** 统一编排部署。

## 🏗 系统架构

本项目包含以下核心服务，通过 **Gateway (Nginx)** 统一对外暴露：

| 服务名称 | 技术栈 | 端口 (内部) | 职责描述 |
| :--- | :--- | :--- | :--- |
| **Gateway** | Nginx | 8080 | 统一 API 网关，负责请求路由转发与跨域处理 |
| **Auth Service** | Go (Gin) | 8081 | 用户注册、登录、JWT 签发、绑定管理 |
| **Edu Service** | Java (Spring Boot) | 8082 | 教务/业务核心服务（学生、教师、班级、课表等） |
| **LLM Service** | Python (FastAPI) | 8000 | 智能对话、敏感词过滤、审计日志、数据看板 |

### 基础设施
- **PostgreSQL**: 存储用户账户、角色信息及教务核心结构化数据。
- **MongoDB**: 存储非结构化数据，如对话历史、敏感词库、审计日志、部分教务冗余数据。
- **Ollama**: 本地大模型推理引擎（需单独部署或配置）。

## ✨ 功能亮点

- **微服务设计**: 各模块职责单一，支持独立部署与扩展，降低耦合。
- **多语言融合**: 
  - **Go**: 高性能处理高频的认证与鉴权请求。
  - **Java**: 成熟生态支撑复杂的教务业务逻辑与事务。
  - **Python**: 灵活处理 AI 对话逻辑与数据分析。
- **智能对话**: 集成 Ollama，支持多种本地模型，低成本私有化部署。
- **安全过滤**: 内置高效 Trie 树敏感词过滤，支持实时热更新，保障合规。
- **角色权限**: 精细化的 RBAC 权限控制（学生/教师/管理员等）及版别控制（教育版/企业版）。

## 🚀 快速开始

### 1. 前置要求
- **Docker** & **Docker Compose**
- **Ollama** (建议在本机安装并运行，默认端口 11434)

### 2. 配置环境
在项目根目录创建 `.env` 文件（可参考以下模板）：

```bash
# === 数据库配置 ===
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=llm_filter_db
MONGODB_URL=mongodb://mongo:27017

# === JWT 安全配置 ===
# 必须生成强随机密钥（建议 32 字节以上）
JWT_SECRET=llm_filter_secure_secret_key_2025_update_must_be_32_bytes
# Auth Service 使用 JWT_SECRET, LLM Service 使用 SECRET_KEY (需保持一致)
SECRET_KEY=llm_filter_secure_secret_key_2025_update_must_be_32_bytes

# === Ollama 配置 ===
# Docker 容器访问宿主机 Ollama 服务
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=deepseek-r1:14b

# === 应用模式 ===
# edu (教育版) / biz (企业版)
APP_MODE=edu
```

### 3. 启动服务
使用 Docker Compose 一键构建并启动所有服务：

```bash
docker-compose up -d --build
```

等待几分钟，直到所有容器启动完成。

### 4. 访问服务
系统统一入口为 **http://localhost:8080**。

#### 📝 API 文档 (Swagger/OpenAPI)
各微服务均提供了在线文档，可通过网关直接访问：

- **Auth Service 文档**: [http://localhost:8080/swagger/index.html](http://localhost:8080/swagger/index.html)
- **Edu Service 文档**: [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)
- **LLM Service 文档**: [http://localhost:8080/docs](http://localhost:8080/docs)

#### 🔌 主要 API 路由
- **认证相关**: `/api/v1/auth/*` (登录、注册)
- **绑定管理**: `/api/v1/bindings/*` (用户-实体绑定)
- **教务管理**: 
  - `/api/v1/edu/*` (综合业务)
  - `/api/v1/classes/*` (班级)
  - `/api/v1/persons/*` (人员档案)
  - `/api/v1/teachers/*` (教师管理)
  - `/api/v1/schedules/*` (课表)
- **对话与看板**: 
  - `/api/v1/conversations/*` (AI 对话)
  - `/api/v1/dashboard/*` (数据看板)
  - `/api/v1/admin/*` (敏感词管理)

## 🛠 开发指南

### 目录结构
```
llm-filter/
├── gateway/                # Nginx 网关配置
├── microservices/
│   ├── auth-service/       # [Go] 认证服务
│   │   ├── internal/       # 业务逻辑
│   │   └── main.go         # 入口文件
│   ├── edu-service/        # [Java] 教务服务
│   │   └── src/main/java/  # Spring Boot 源码
│   └── llm-service/        # [Python] LLM与过滤服务
│       └── app/            # FastAPI 源码
├── docker-compose.yml      # 容器编排文件
└── README.md               # 项目文档
```

### 本地独立开发
若需单独开发某个微服务，请参考各子目录下的 README 或直接运行：

- **Auth Service**: 进入 `microservices/auth-service`，运行 `go run main.go`
- **Edu Service**: 进入 `microservices/edu-service`，运行 `mvn spring-boot:run`
- **LLM Service**: 进入 `microservices/llm-service`，运行 `uvicorn app.main:app --reload`

*注意：本地独立运行时需确保依赖的数据库（Postgres/Mongo）已启动并配置正确的连接地址。*

## 📄 许可证
MIT License
