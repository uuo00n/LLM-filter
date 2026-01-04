# LLM Filter 项目启动与开发指南

本文档旨在帮助开发人员快速搭建环境、启动服务并参与开发。本项目采用微服务架构，包含以下服务组件：

1.  **Gateway (Nginx)**: 统一入口网关，负责路由分发。
2.  **Auth Service (Go)**: 身份认证与用户管理服务。
3.  **Edu Service (Java)**: 教务核心业务服务。
4.  **LLM Service (Python)**: 大模型交互与编排服务。
5.  **Security Service (Python)**: 安全分析与风险监控服务。

---

## 快速启动（Docker）

### 前置要求
- Docker & Docker Compose
- 可选：根目录 `.env`（建议生产/团队环境使用，避免把密钥写进配置文件）

### 启动命令
在项目根目录执行：

```bash
# 构建并后台启动所有服务
docker-compose up -d --build

# 查看运行日志
docker-compose logs -f
```

### 访问服务
- **统一入口（网关）**: [http://localhost:8080](http://localhost:8080)
- **文档聚合入口**:
    - **Security Swagger**: [http://localhost:8080/docs/security/](http://localhost:8080/docs/security/)
    - **LLM Swagger**: [http://localhost:8080/docs/llm/](http://localhost:8080/docs/llm/)
    - **Edu Swagger**: [http://localhost:8080/docs/edu/](http://localhost:8080/docs/edu/)
    - **Auth Swagger**: [http://localhost:8080/docs/auth/](http://localhost:8080/docs/auth/)

端口约定（Docker 外部映射）：
- Gateway: 8080
- Auth Service: 8081
- Edu Service: 8082
- LLM Service: 8000
- Security Service: 8003

---

## 本地开发指南

如果你需要修改代码，建议在本地分别启动服务。

### 1. 启动基础设施 (数据库)
首先确保数据库在运行。你可以只通过 Docker 启动 DB：

```bash
# 启动 Postgres 和 Mongo
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

# 运行服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动 Security Service (Python)
**目录**: `microservices/security-service`
**要求**: Python 3.10+

```bash
cd microservices/security-service

# 创建虚拟环境 (可选)
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行服务 (建议使用 8003 端口以避免冲突)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

---

## 接口测试流程

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
LLM Service 会在本地校验 JWT（要求 `SECRET_KEY` 与 Auth Service 的 `JWT_SECRET` 保持一致）。

```bash
# 1) 创建对话，拿到 conversation_id
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json"

# 2) 向对话发送消息
curl -X POST http://localhost:8000/api/v1/conversations/<CONVERSATION_ID>/messages \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"content": "你好，请介绍一下你自己"}'
```

### 4. 安全服务操作 (Security Service)
Security Service 同样校验 JWT。

```bash
# 1) 查询历史分析记录 (需管理员权限)
curl "http://localhost:8003/api/v1/security/analysis/history?limit=5" \
  -H "Authorization: Bearer <TOKEN>"

# 2) 提交新的风险分析请求
curl -X POST "http://localhost:8003/api/v1/security/analysis" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {"name": "Core-Switch", "ip": "192.168.1.1", "status": "online", "logs": "high traffic"}
    ]
  }'
```

---

## 目录结构说明

```text
/llm-filter
├── gateway/                # Nginx 网关配置
├── docker-compose.yml        # 容器编排文件
├── .env                      # 全局环境变量 (数据库密码、密钥等)
└── microservices/            # 微服务源码目录
    ├── auth-service/         # [Go] 认证服务
    ├── edu-service/          # [Java] 教务服务
    ├── llm-service/          # [Python] LLM 核心服务
    └── security-service/     # [Python] 安全分析服务
```

## 常见问题

1.  **端口冲突**：如果 `5432` 被本地 Postgres 占用，Docker 会映射到 `5433`。代码中已默认适配 `5433`，如需修改请检查 `.env` 和各服务的配置文件。
2.  **Maven 下载慢**：请使用项目提供的 `microservices/edu-service/settings.xml`，已配置阿里云镜像。
3.  **鉴权失败 (401)**：请确保所有服务 (`.env` 或配置文件中) 的 `JWT_SECRET` / `SECRET_KEY` 保持一致。

