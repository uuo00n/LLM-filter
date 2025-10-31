# LLM-Filter 智能对话过滤系统

## 项目概述

LLM-Filter 是一个基于大型语言模型(LLM)的智能对话系统，集成了敏感词过滤功能，可以安全地与用户进行对话交互。系统通过 Ollama 本地模型提供对话能力，同时实现了高效的敏感词检测和过滤，确保生成的内容符合安全标准。

### 核心功能特点

- **智能对话**：基于 Ollama 本地大语言模型提供自然、流畅的对话体验
- **敏感词过滤**：使用高效的 Trie 树数据结构实现敏感词检测和过滤
- **用户管理**：支持用户注册、登录和权限管理
- **对话历史**：保存和管理用户的对话历史记录
- **敏感词管理**：提供敏感词的添加、删除和查询功能
- **敏感记录追踪**：记录并可查询敏感词触发情况

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
- `GET /api/v1/sensitive-words` - 获取所有敏感词
- `GET /api/v1/sensitive-records` - 获取敏感词记录

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

[指定许可证类型]

## 联系方式

[提供联系信息]