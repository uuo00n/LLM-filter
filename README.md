# LLM-Filter 智能对话过滤系统

## 项目概述

LLM-Filter 是一个基于大型语言模型(LLM)的智能对话系统，集成了敏感词过滤功能，可以安全地与用户进行对话交互。系统通过 Ollama 本地模型提供对话能力，同时实现了高效的敏感词检测和过滤，确保生成的内容符合安全标准。

### 核心功能特点

- **智能对话**：基于 Ollama 本地大语言模型提供自然、流畅的对话体验
- **敏感词过滤**：使用高效的 Trie 树数据结构实现敏感词检测和过滤
- **用户管理**：支持用户注册、登录和权限管理
- **对话历史**：保存和管理用户的对话历史记录
- **敏感词管理**：提供敏感词的添加、删除和查询功能
- **敏感词分类**：支持敏感词分类和子分类管理，可按类别筛选
- **批量导入**：支持批量导入敏感词，提高管理效率
- **敏感记录追踪**：记录并可查询敏感词触发情况，支持多维度筛选

## 系统架构

### 技术栈

- **后端框架**：FastAPI
- **数据库**：MongoDB
- **大语言模型**：Ollama (本地部署)
- **认证**：JWT (JSON Web Token)
- **文档**：Swagger UI / ReDoc

### 核心组件

- **API 层**：处理 HTTP 请求和响应
- **服务层**：实现业务逻辑
- **数据模型层**：定义数据结构
- **工具层**：提供敏感词过滤等功能
- **数据库层**：处理数据持久化

### 数据库结构

系统使用MongoDB作为数据库，包含以下集合：

#### 1. users 集合

用户信息存储，包含字段：
- `_id`: 用户唯一标识
- `username`: 用户名
- `email`: 电子邮箱
- `hashed_password`: 加密后的密码
- `role`: 用户角色，可为 "user" 或 "admin"
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 2. conversations 集合

对话信息存储，包含字段：
- `_id`: 对话唯一标识
- `user_id`: 关联的用户ID
- `messages`: 消息列表，每条消息包含：
  - `role`: 消息角色，可为 "user" 或 "assistant"
  - `content`: 消息内容
  - `timestamp`: 消息时间戳
  - `contains_sensitive_words`: 是否包含敏感词
  - `sensitive_words_found`: 发现的敏感词列表
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 3. sensitive_words 集合

敏感词信息存储，包含字段：
- `_id`: 敏感词唯一标识
- `word`: 敏感词内容
- `category`: 敏感词主分类（如"违法活动"、"不良内容"等）
- `subcategory`: 敏感词子分类（如"赌博"、"自杀"等）
- `severity`: 严重程度（1-5级，5为最严重）
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 4. sensitive_records 集合

敏感词检测记录，包含字段：
- `_id`: 记录唯一标识
- `user_id`: 关联的用户ID
- `conversation_id`: 关联的对话ID
- `message_content`: 触发检测的消息内容
- `sensitive_words_found`: 发现的敏感词详细信息列表，每项包含：
  - `word`: 敏感词
  - `category`: 主分类
  - `subcategory`: 子分类
  - `severity`: 严重程度
- `highest_severity`: 记录中最高的严重程度
- `timestamp`: 记录时间

## 安装与配置

### 环境要求

- Python 3.9+
- MongoDB
- Ollama (本地安装)

### 安装步骤

1. 克隆项目仓库

   ```bash
   git clone <repository-url>
   cd llm-filter
   ```
2. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量
   创建 `.env` 文件并设置以下变量：

   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=llm_filter
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   OLLAMA_API_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   ```

   **生成安全的SECRET_KEY**
   
   为了确保系统安全，请使用以下方法生成一个强随机密钥：

   ```python
   # 在Python终端中运行
   import secrets
   print(secrets.token_hex(32))  # 生成一个64字符的随机十六进制字符串
   ```

   或者使用命令行：

   ```bash
   # Linux/Mac
   openssl rand -hex 32
   
   # 或者
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   将生成的密钥复制到`.env`文件的`SECRET_KEY`变量中。
4. 初始化数据库

   ```bash
   python init_db.py
   ```
5. 启动应用

   ```bash
   uvicorn app.main:app --reload
   ```

## API 端点

### 用户相关

- `POST /api/v1/users/register` - 用户注册
- `POST /api/v1/users/login` - 用户登录
- `GET /api/v1/users/me` - 获取当前用户信息

### 对话相关

- `POST /api/v1/conversations` - 创建新对话
- `GET /api/v1/conversations` - 获取用户所有对话
- `GET /api/v1/conversations/{conversation_id}` - 获取特定对话详情
- `POST /api/v1/conversations/{conversation_id}/messages` - 发送消息

### 敏感词相关

- `POST /api/v1/sensitive-words` - 添加敏感词
- `DELETE /api/v1/sensitive-words/{word_id}` - 删除敏感词
- `GET /api/v1/sensitive-words` - 获取所有敏感词（支持按类别、子类别和严重程度筛选）
- `GET /api/v1/sensitive-records` - 获取敏感词记录（支持按用户、对话、时间范围、类别、子类别和严重程度筛选）

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
│   └── utils/              # 工具函数
├── init_db.py              # 数据库初始化脚本
└── requirements.txt        # 项目依赖
```

## 核心模块说明

### 敏感词过滤器

系统使用 Trie 树（字典树）实现高效的敏感词检测：

- `TrieNode` 类：实现 Trie 树的节点结构
- `SensitiveWordFilter` 类：提供敏感词加载和检测功能

#### 敏感词分类系统

敏感词采用多层分类体系，便于管理和筛选：

1. **主分类**：包括违法活动、不良内容、政治内容、歧视言论、暴力内容、色情内容、毒品相关、赌博相关、诈骗相关等
2. **子分类**：每个主分类下设多个子分类，如：
   - 违法活动：贩毒、赌博、诈骗、传销等
   - 不良内容：自杀、自残、暴力、血腥等
   - 歧视言论：种族歧视、性别歧视、地域歧视等
3. **严重程度**：1-5级，5级为最严重

这种分类系统使管理员能够：
- 精确定位和管理敏感内容
- 按类别和严重程度筛选敏感记录
- 针对不同类型的敏感内容制定不同的处理策略

### 对话服务

对话功能通过以下组件实现：

- `ConversationModel` 和 `MessageModel`：定义对话和消息的数据结构
- `add_message` 函数：处理用户消息，检测敏感词，生成 AI 回复
- `generate_response` 函数：调用 Ollama API 生成回复

### 用户认证

使用 JWT 实现用户认证：

- `create_access_token` 函数：生成访问令牌
- `get_current_user` 函数：验证用户身份

## 使用示例

### 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123", "email": "test@example.com"}'
```

### 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123"}'
```

### 创建对话

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
     -H "Authorization: Bearer {your_token}" \
     -H "Content-Type: application/json" \
     -d '{}'
```

### 发送消息

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/{conversation_id}/messages" \
     -H "Authorization: Bearer {your_token}" \
     -H "Content-Type: application/json" \
     -d '{"content": "你好，请问今天天气如何？"}'
```

## 开发者指南

### 添加新的敏感词

1. 通过 API 添加
2. 直接在数据库中添加

### 自定义 Ollama 模型

修改 `.env` 文件中的 `OLLAMA_MODEL` 变量以使用不同的模型。

## 许可证

MIT License

Copyright (c) 2025 uuo00_n

## 联系方式

作者：uuo00_n
