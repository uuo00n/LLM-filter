# 🚀 LLM Filter 项目开发与启动指南

本文档旨在帮助开发人员快速搭建环境、启动服务并参与开发。本项目采用微服务架构，包含 Auth (Go), Edu (Java), LLM (Python) 三大核心服务。

---

## 🏗️ 架构概览

| 服务名称 | 端口 | 技术栈 | 职责 | 目录 |
| :--- | :--- | :--- | :--- | :--- |
| **Auth Service** | **8081** | Go (Gin) | 用户认证、JWT、绑定管理 | `microservices/auth-service` |
| **Edu Service** | **8082** | Java (Spring Boot) | 学生、教师、课表、教务数据 | `microservices/edu-service` |
| **LLM Service** | **8000** | Python (FastAPI) | AI 对话、RAG、敏感词过滤 | `microservices/llm-service` |
| **Postgres** | 5433 | PostgreSQL 15 | 存储 Auth 和 Edu 数据 | (Docker) |
| **Mongo** | 27017 | MongoDB | 存储对话历史、敏感词库 | (Docker) |

---

## ⚡ 快速启动 (Docker 模式)

这是最简单的启动方式，适合预览或部署。

### 前置要求
- Docker & Docker Compose
- 根目录下已配置 `.env` 文件

### 启动命令
在项目根目录执行：

```bash
# 构建并后台启动所有服务
docker-compose up -d --build

# 查看运行日志
docker-compose logs -f
```

### 访问服务
- **Swagger 文档 (LLM)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Auth API**: [http://localhost:8081/api/v1/auth/health](http://localhost:8081/api/v1/auth/health)
- **Edu API**: [http://localhost:8082/api/v1/edu/health](http://localhost:8082/api/v1/edu/health)

---

## 🛠️ 本地开发指南 (Local Development)

如果你需要修改代码，建议在本地分别启动服务。

### 1. 启动基础设施 (数据库)
首先确保数据库在运行。你可以只通过 Docker 启动 DB：

```bash
# 只启动 Postgres 和 Mongo
docker-compose up -d postgres mongo
```

### 2. 启动 Auth Service (Go)
**目录**: `microservices/auth-service`

```bash
cd microservices/auth-service

# 安装依赖
go mod tidy

# 运行服务 (确保本地 5433 端口可用)
# 注意：代码中已配置连接 localhost:5433
go run main.go
```

### 3. 启动 Edu Service (Java)
**目录**: `microservices/edu-service`
**要求**: JDK 1.8, Maven

```bash
cd microservices/edu-service

# 编译并运行 (指定 settings.xml 以使用阿里云镜像)
mvn -s settings.xml clean spring-boot:run
```

### 4. 启动 LLM Service (Python)
**目录**: `microservices/llm-service`
**要求**: Python 3.10+

```bash
cd microservices/llm-service

# 创建虚拟环境 (可选)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务 (会自动向上查找根目录的 .env)
python main.py
```

---

## 🧪 接口测试流程

### 1. 注册与登录 (Auth Service)
所有操作都需要 Token。

```bash
# 1. 注册
curl -X POST http://localhost:8081/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123", "email": "test@example.com"}'

# 2. 登录 (获取 Token)
curl -X POST http://localhost:8081/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

### 2. 教务数据操作 (Edu Service)
使用上一步获取的 Token (`Bearer <TOKEN>`)。

```bash
# 列出班级
curl http://localhost:8082/api/v1/classes \
  -H "Authorization: Bearer <TOKEN>"
```

### 3. AI 对话 (LLM Service)
LLM Service 会自动调用 Auth Service 验证 Token。

```bash
# 发起对话
curl -X POST http://localhost:8000/api/v1/conversations/chat \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下你自己"}'
```

---

## 📂 目录结构说明

```text
/llm-filter
├── docker-compose.yml        # 容器编排文件
├── .env                      # 全局环境变量 (数据库密码、密钥等)
└── microservices/            # 微服务源码目录
    ├── auth-service/         # [Go] 认证服务
    ├── edu-service/          # [Java] 教务服务
    └── llm-service/          # [Python] LLM 核心服务
```

## ⚠️ 常见问题

1.  **端口冲突**：如果 `5432` 被本地 Postgres 占用，Docker 会映射到 `5433`。代码中已默认适配 `5433`，如需修改请检查 `.env` 和各服务的配置文件。
2.  **Maven 下载慢**：请使用项目提供的 `microservices/edu-service/settings.xml`，已配置阿里云镜像。
3.  **Python 找不到 .env**：`config.py` 已内置自动向上查找逻辑，确保在 `microservices/llm-service` 目录下运行即可。
