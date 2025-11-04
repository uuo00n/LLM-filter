# LLM-Filter 智能对话过滤系统

一个基于 FastAPI + MongoDB + Ollama 的智能对话系统，内置高效敏感词过滤与管理员管理能力。

## 功能亮点
- 智能对话：基于本地 Ollama 模型生成回复
- 敏感词过滤：Trie（字典树）实现高效检测与标记
- 用户认证：JWT（OAuth2 密码模式），支持普通用户与管理员
- 对话历史：按用户保存会话与消息
- 敏感词管理：管理员可增删改查、批量导入、按分类/严重程度筛选
- 敏感记录追踪：记录触发详情与严重等级

---

## 兼容性与系统要求
- Python 3.9+
- MongoDB 6.x 或 7.x（推荐 7.0；6.0 也可正常使用）
- Ollama（推荐在本机安装并运行，默认端口 11434）

> 驱动版本：PyMongo 4.6.0、Motor 3.3.1，已在 MongoDB 6/7 验证兼容。

---

## 快速开始（Mac 示例）

1) 创建并激活虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate
python -V  # 确认 Python 版本
```

2) 安装依赖
```bash
pip install -r requirements.txt
```

3) 配置环境变量（.env）
在项目根目录新建或编辑 `.env`：
```
# 数据库配置
MONGODB_URL=mongodb://localhost:27017
DB_NAME=llm_filter_db

# JWT配置
SECRET_KEY=请替换为强随机密钥
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```
生成强随机密钥（二选一）：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# 或
openssl rand -hex 32
```
将输出填入 `.env` 的 SECRET_KEY。

4) 启动 MongoDB（任选其一）
```bash
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
# 或 6.0 版本：
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```
确认端口：
```bash
nc -z localhost 27017 && echo "MongoDB is running" || echo "MongoDB is NOT running"
```

5) 启动 Ollama 并确认（可选但推荐）
```bash
# 安装 Ollama（参考官方文档）
# 验证服务：
curl http://localhost:11434/api/tags
```
如需模型：
```bash
# 例如拉取 llama2（需网络）
ollama pull llama2
```

6) 初始化数据库（创建演示数据与默认账户）
```bash
python init_db.py
```
默认测试账号：
- 管理员：admin / admin123
- 普通用户：user / user123

7) 启动服务
```bash
uvicorn app.main:app --reload
# 访问文档: http://localhost:8000/docs
```

---

## 环境变量说明
与代码一致，配置由 `app/core/config.py` 读取：
- MONGODB_URL：MongoDB 连接串，默认 `mongodb://localhost:27017`
- DB_NAME：数据库名，默认 `llm_filter_db`
- SECRET_KEY：JWT 签名密钥（必须为强随机）
- ALGORITHM：JWT 算法，默认 `HS256`
- ACCESS_TOKEN_EXPIRE_MINUTES：访问令牌过期时间（分钟），默认 `30`
- OLLAMA_BASE_URL：Ollama 服务地址，默认 `http://localhost:11434`
- OLLAMA_MODEL：Ollama 模型名，默认 `llama2`

> 注意：原 README 中的 `DATABASE_NAME`、`OLLAMA_API_BASE_URL` 为旧命名，现统一为 `DB_NAME` 与 `OLLAMA_BASE_URL`。

---

## API 概览
根路径：`/` 返回应用信息
统一前缀：`/api/v1`

### 认证（/auth）
- POST `/api/v1/auth/register` 注册用户（JSON）
- POST `/api/v1/auth/login` 登录，返回 `access_token`（表单：`application/x-www-form-urlencoded`）

示例：注册
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123", "email": "test@example.com"}'
```
示例：登录（OAuth2 密码模式）
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123"
# 响应示例：{"access_token":"<JWT>","token_type":"bearer"}
```
获取到 `access_token` 后，在后续请求头添加：
```
Authorization: Bearer <JWT>
```

### 对话（/conversations）
- POST `/api/v1/conversations/` 创建新对话
- GET `/api/v1/conversations/` 获取当前用户的所有对话
- GET `/api/v1/conversations/{conversation_id}` 获取指定对话
- POST `/api/v1/conversations/{conversation_id}/messages` 发送消息并获取回复

示例：创建对话
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/" \
     -H "Authorization: Bearer <JWT>"
```
示例：发送消息
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/<ID>/messages" \
     -H "Authorization: Bearer <JWT>" \
     -H "Content-Type: application/json" \
     -d '{"content": "你好，你是谁？"}'
# 响应会包含是否触发敏感词与模型回复
```

### 管理员（/admin）
仅管理员可用，需使用管理员账号登录并携带 `Authorization: Bearer <JWT>`。
- POST `/api/v1/admin/sensitive-words` 添加敏感词
- DELETE `/api/v1/admin/sensitive-words/{word_id}` 删除敏感词
- GET `/api/v1/admin/sensitive-words` 查询敏感词（支持分类/子分类/严重程度筛选）
- POST `/api/v1/admin/sensitive-words/bulk` 批量添加敏感词
- POST `/api/v1/admin/sensitive-words/import` 从 CSV/JSON 文件导入敏感词
- GET `/api/v1/admin/sensitive-records` 查询敏感词触发记录（支持多维度筛选）
- 分类相关：
  - GET `/api/v1/admin/categories` 获取所有分类
  - GET `/api/v1/admin/categories/default` 获取默认分类与子分类
  - POST `/api/v1/admin/categories` 新增分类
  - PUT `/api/v1/admin/categories/{category_name}` 更新分类子分类
  - DELETE `/api/v1/admin/categories/{category_name}` 删除分类

CSV 导入示例（文件需包含表头：word,category,subcategory,severity）：
```bash
curl -X POST "http://localhost:8000/api/v1/admin/sensitive-words/import" \
     -H "Authorization: Bearer <JWT>" \
     -F "file=@/path/to/words.csv"
```
JSON 导入示例（数组对象）：
```bash
curl -X POST "http://localhost:8000/api/v1/admin/sensitive-words/import" \
     -H "Authorization: Bearer <JWT>" \
     -F "file=@/path/to/words.json"
# words.json 示例：[ {"word":"赌博","category":"违法活动","subcategory":"赌博","severity":3} ]
```

---

## 项目结构
```
llm-filter/
├── .env                    # 环境变量配置
├── app/                    # 应用主目录
│   ├── api/                # API 路由
│   │   └── v1/             # API 版本
│   ├── core/               # 核心配置
│   ├── db/                 # 数据库连接
│   ├── models/             # 数据模型
│   ├── schemas/            # 请求和响应模式
│   ├── services/           # 业务服务
│   └── utils/              # 工具函数（敏感词过滤）
├── init_db.py              # 数据库初始化脚本
└── requirements.txt        # 项目依赖
```

---

## 敏感词过滤说明
- 使用 Trie（字典树）加载敏感词并检测文本，返回是否命中与命中的词列表
- 支持主分类与子分类，并记录严重程度（1-5，5 最严重）
- 管理员可通过导入/批量添加快速构建词库

---

## 开发与部署提示
- CORS 已默认允许全部来源，生产环境请限制 `allow_origins`
- 开发模式使用 `--reload`；生产建议使用 `uvicorn`/`gunicorn` + 进程管理（如 `supervisor`/`systemd`）
- 日志与安全：请务必使用强随机 `SECRET_KEY` 并妥善保管 `.env`

---

## 常见问题（FAQ）
1) 登录始终 401？
- 确保使用 `application/x-www-form-urlencoded` 提交登录：`username=...&password=...`
- 后续请求携带 `Authorization: Bearer <JWT>`

2) 连接 MongoDB 失败？
- 检查 `MONGODB_URL` 与数据库端口是否开放：`nc -z localhost 27017`
- 本地安装服务建议：`brew services start mongodb-community@6.0/7.0`

3) Ollama 连接失败？
- 检查 `OLLAMA_BASE_URL` 是否指向可用服务：`curl http://localhost:11434/api/tags`
- 确保已拉取并可用的模型（如 `ollama pull llama2`）

---

## 许可证
本项目使用 MIT 许可证，详见 `LICENSE`。

## 贡献
欢迎提交 Issue 与 PR，一起完善敏感词分类与对话体验。