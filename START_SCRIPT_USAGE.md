# LLM Filter 启动脚本使用说明

本文档说明项目唯一启动脚本 `start.sh` 的使用方式。

## 1. 前置要求

- Docker
- Docker Compose（支持 `docker compose` 或 `docker-compose`）
- Python3（用于首次生成 `.env`）

## 2. 快速开始

```bash
# 1) 首次生成 .env
./start.sh init-env

# 2) 启动全部服务并初始化演示数据
./start.sh up --init-data

# 3) 查看状态
./start.sh ps
```

## 3. .env 生成与使用

### 3.1 生成 `.env`

```bash
./start.sh init-env
```

脚本会调用 `scripts/generate_secrets.py` 自动生成根目录 `.env`。

### 3.2 修改 `.env`

生成后建议至少确认以下配置：

- `DB_PASSWORD`
- `JWT_SECRET`
- `DIFY_API_KEY_LLM`
- `DIFY_API_KEY_SECURITY`

### 3.3 生效方式

`.env` 修改后需要重启容器：

```bash
./start.sh down
./start.sh up
```

或仅重构指定服务容器：

```bash
./start.sh rebuild auth-service
```

## 4. 常用命令

```bash
./start.sh help            # 查看帮助
./start.sh init-env        # 生成 .env（首次）
./start.sh up              # 构建并启动所有服务（不初始化数据）
./start.sh up --init-data  # 启动后自动执行数据库初始化脚本
./start.sh init-data       # 单独执行数据库初始化脚本（会提示确认）
./start.sh init-data --yes # 单独执行数据库初始化脚本（跳过确认）
./start.sh rebuild         # 重构全部服务容器
./start.sh rebuild gateway # 重构指定服务容器
./start.sh down            # 停止并删除容器
./start.sh rm gateway      # 删除指定容器（可传多个服务）
./start.sh reset           # 停止并删除容器+数据卷（清空数据库）
./start.sh ps              # 查看容器状态
./start.sh logs            # 查看全部日志
./start.sh logs gateway    # 查看单个服务日志
```

## 5. 访问地址

- 网关入口：`http://localhost:8080`
- Auth 文档：`http://localhost:8080/docs/auth/`
- Edu 文档：`http://localhost:8080/docs/edu/`
- LLM 文档：`http://localhost:8080/docs/llm/`
- Security 文档：`http://localhost:8080/docs/security/`

## 6. 常见问题

### 6.1 `.env` 无法读取（权限问题）

如果之前用 `sudo` 生成过 `.env`，可能出现权限错误：

```bash
sudo chown $USER:staff .env
chmod 640 .env
```

### 6.2 数据库密码不匹配导致服务启动失败

若日志出现数据库认证失败（如 `password authentication failed`），可二选一：

1. 把 `.env` 的 `DB_PASSWORD` 改回旧值再重启
2. 清空数据卷重建（会删除数据库数据）：

```bash
./start.sh reset
./start.sh up
```

### 6.3 为什么没有默认账号（如 `admin_edu`）

默认 `./start.sh up` 不会自动执行 `scripts/init_postgres.sql` 和其他初始化脚本。  
如需写入演示账号/数据，请执行：

```bash
./start.sh init-data
```
