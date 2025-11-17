# LLM-Filter 智能对话过滤系统

一个面向教育与企业双场景的智能对话系统，基于 FastAPI + MongoDB + Ollama 构建，内置高效敏感词过滤、严格的角色与版别控制、完善的管理员操作与审计能力。

本文档面向开发者与运维人员，提供从架构到部署的完整说明与最佳实践。

## 功能亮点
- 智能对话：基于本地 Ollama 模型生成回复，支持可配置模型与服务地址
- 敏感词过滤：Trie（字典树）实现高效检测与标记，支持分类/子分类与严重程度
- 用户认证：JWT（OAuth2 密码模式），支持普通用户与管理员，令牌过期可配置
- 对话历史：按用户维度保存会话与消息，记录敏感命中与模型回复
- 敏感词管理：管理员增删改查、批量导入、CSV/JSON 文件导入与热更新
- 审计追踪：敏感词触发记录，含最高严重度与触发上下文，便于合规审计
- 实体化数据模型：账号与人物分离，学生/教师等实体通过主绑定统一管理
- 角色看板：按角色等级与实体身份提供学生/班主任/中层/校级数据接口

---

## 系统架构
- 应用层：`FastAPI` 提供 RESTful API，统一前缀 `\u002Fapi\u002Fv1`
- 模型层：`Ollama` 作为本地推理服务，通过 `OLLAMA_BASE_URL` 与 `OLLAMA_MODEL` 配置
- 数据层：`MongoDB` 存储账户、实体、课表与对话相关数据，敏感词词库与审计记录亦存于此
- 过滤层：在应用内维护 Trie 结构，服务启动与词库变更时自动加载与热更新
- 认证授权：`OAuth2 Password` + `JWT`，基于角色与版别依赖限制路由访问

数据流概览：
- 用户登录获取 `access_token` → 创建对话 → 发送消息 → 文本先经 Trie 过滤与记录 → 再调用 Ollama 获取回复 → 返回综合结果并持久化

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
APP_MODE=edu
# 初始密码（可选，未设置时使用默认值）：
ADMIN_EDU_PASSWORD=admin123
USER_EDU_PASSWORD=user123
MANAGER_EDU_PASSWORD=manager123
LEADER_EDU_PASSWORD=leader123
MASTER_EDU_PASSWORD=master123
# 企业版对应：ADMIN_BIZ_PASSWORD/USER_BIZ_PASSWORD/MANAGER_BIZ_PASSWORD/LEADER_BIZ_PASSWORD/MASTER_BIZ_PASSWORD
```
生成强随机密钥（二选一）：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# 或
openssl rand -hex 32
```
将输出填入 `.env` 的 `SECRET_KEY`。

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

6) 初始化数据库（创建演示数据与默认账户与实体化数据）
```bash
python init_db.py
```
默认测试账号：
- 管理员：admin / admin123
- 普通用户：user / user123

实体化初始化内容：
- 生成 students/classes/schedules/attendance/conduct/leaves/directives
- 生成 persons（为每位学生生成人物档案）与 teachers（示例教师/班主任/干部）
- 生成 bindings（账号与人物主绑定），并清理旧字段与索引（students.user_id/classes.head_teacher_id/schedules.teacher_id）

重要说明：
- 该脚本会清空 `DB_NAME` 指定库中的所有集合（drop collection），随后再写入演示数据，仅用于本地开发与测试，请勿在生产环境运行。
- 版别通过环境变量 `APP_MODE` 控制（可选值：`edu` 或 `biz`，默认 `edu`）。脚本仅插入当前模式对应的测试用户，路由亦基于该模式限制访问版别。

7) 启动服务
```bash
uvicorn app.main:app --reload
# 访问文档: http://localhost:8000/docs
```

---

## 配置详解
与代码一致，配置由 `app/core/config.py` 读取：
- `MONGODB_URL`：MongoDB 连接串，默认 `mongodb://localhost:27017`
- `DB_NAME`：数据库名，默认 `llm_filter_db`
- `APP_MODE`：应用运行版别，`edu` 或 `biz`，默认 `edu`；路由依赖限制仅允许当前版别访问
- `SECRET_KEY`：JWT 签名密钥（必须为强随机），建议长度 ≥ 32 字节
- `ALGORITHM`：JWT 算法，默认 `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`：访问令牌过期时间（分钟），默认 `30`，生产环境建议缩短并启用刷新策略
- `OLLAMA_BASE_URL`：Ollama 服务地址，默认 `http://localhost:11434`
- `OLLAMA_MODEL`：Ollama 模型名，默认 `llama2`

> 命名统一：旧命名 `DATABASE_NAME`、`OLLAMA_API_BASE_URL` 已替换为 `DB_NAME` 与 `OLLAMA_BASE_URL`。

启动顺序与依赖：
- 读取 `.env` → 建立 MongoDB 连接 → 加载敏感词至 Trie → 注册路由与依赖 → 启动服务并可用

---

## API 概览
- 根路径：`/` 返回应用信息
- 统一前缀：`/api/v1`

认证与调用约定：
- 登录接口返回 `access_token` 与 `token_type`，后续请求在头部携带 `Authorization: Bearer <JWT>`
- 管理员接口需具备管理员角色与与 `APP_MODE` 一致的版别，否则返回 403/401

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

说明：部分路由挂载了基于 `APP_MODE` 的版别限制依赖（`require_edition_for_mode`），仅允许与当前模式一致的用户访问。

CSV 导入示例（文件需包含表头：`word,category,subcategory,severity`）：
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

### 仪表盘（/dashboard）
- GET `/api/v1/dashboard/student/today` 学生端：今日个人课表、出勤与操行（需角色≥1且主绑定为学生）
- GET `/api/v1/dashboard/homeroom/current` 班主任端：当前节次课程与地点、节次出勤率、请假、部门指示（需角色≥2且主绑定为教师）
- GET `/api/v1/dashboard/department/overview` 中层端：教师节次出勤率、学生出勤聚合、异常班级、近期指示（需角色≥3）
- GET `/api/v1/dashboard/campus/overview` 校级端：校园整体总览（需角色≥5）

说明：路由统一挂载版别限制依赖 `require_edition_for_mode()`，学生/班主任端同时挂载实体绑定依赖 `require_binding(student|teacher)`。

### 人员与实体管理
- 人物档案（/persons）
  - POST `/api/v1/persons/bulk` 批量导入人物档案（`person_id/name/type`）
  - GET `/api/v1/persons` 列出人物档案
- 教师实体（/teachers）
  - POST `/api/v1/teachers/bulk` 批量导入教师实体（`person_id/teacher_id/department/roles`，可选 `account_id`）
  - GET `/api/v1/teachers` 列出教师实体
- 绑定管理（/bindings）
  - POST `/api/v1/bindings` 创建主绑定（`type=student|teacher`）
  - DELETE `/api/v1/bindings/{person_id}` 删除绑定
  - GET `/api/v1/bindings/me` 查询当前账号主绑定
- 班级管理（/classes）
  - PUT `/api/v1/classes/{class_id}/head-teacher` 设置 `head_teacher_person_id`
  - GET `/api/v1/classes` 列出班级
- 课表管理（/schedules）
  - PUT `/api/v1/schedules/assign-teacher` 设置 `teacher_person_id`
  - GET `/api/v1/schedules` 列出共享节次（含各班 `location`）

---

## 项目结构
```
llm-filter/
├── .env                    # 环境变量配置
├── app/                    # 应用主目录
│   ├── api/                # API 路由
│   │   └── v1/             # API 版本
│   │       ├── dashboard.py     # 仪表盘数据接口（按角色）
│   │       ├── bindings.py      # 账号与人物绑定管理
│   │       ├── persons.py       # 人物档案管理
│   │       ├── teachers.py      # 教师实体管理
│   │       ├── classes.py       # 班级管理（班主任人物）
│   │       ├── schedules.py     # 课表管理（共享节次/教师人物）
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

## 数据模型与集合说明
- `users`：账户与认证信息，用于登录与权限控制；字段包含 `username/email/hashed_password/role/role_level/edition/created_at/updated_at`。
- `persons`：人物档案的统一身份标识；字段包含 `person_id/name/type`，供学生/教师等实体引用。
- `bindings`：账号与人物的主绑定关系；字段包含 `account_id/person_id/type/primary`，决定账号当前实体身份（学生/教师）。
- `students`：学生实体信息；字段包含 `student_id/name/gender/grade/major/class_id/status/person_id/created_at/updated_at`。
- `teachers`：教师实体信息；字段包含 `teacher_id/department/roles/account_id/person_id`，`roles` 示例：`teacher/homeroom/cadre`。
- `classes`：班级基础信息；字段包含 `class_id/name/grade/major/students_count/head_teacher_person_id`。
- `schedules`：共享节次与课程安排；字段包含 `lesson_id/weekday/period/course_name/teacher_person_id/start_time/end_time/week_range/classes[class_id/location]`。
- `attendance`：学生出勤记录；字段包含 `lesson_id/class_id/student_id/date/status`。
- `conduct`：操行与德育评分；字段包含 `student_id/date/metrics{...}/teacher_comment/head_teacher_comment/score`。
- `leaves`：学生请假记录；字段包含 `student_id/class_id/from_date/to_date/reason/approved_by/status`。
- `directives`：部门/校园指示公告；字段包含 `level/content/issuer_id/targets/created_at`，`level` 示例：`department/campus`。
- `conversations`：用户对话与消息历史；字段包含 `user_id/messages[role/content/timestamp/contains_sensitive_words/sensitive_words_found]/created_at/updated_at`。
- `sensitive_words`：敏感词词库；字段包含 `word/category/subcategory/severity/created_at/updated_at`，用于构建内存 Trie。
- `sensitive_records`：敏感词触发审计日志；字段包含 `user_id/conversation_id/message_content/sensitive_words_found/highest_severity/timestamp`。

说明与关系要点：
- 账户（`users`）与人物（`persons`）分离，通过 `bindings` 形成账号的主实体身份。
- 学生（`students`）隶属班级（`classes`），课程排程（`schedules`）由教师人物负责并面向多个班级。
- 出勤（`attendance`）、操行（`conduct`）、请假（`leaves`）与指示（`directives`）共同支撑角色仪表盘的数据聚合。

### 集合读写与路由映射
- `users`：写 `register`/初始化；读认证与会话用户；路由 `/api/v1/auth/*`
- `persons`：写 批量导入与初始化；读 列表与绑定引用；路由 `/api/v1/persons*`
- `bindings`：写 创建/删除主绑定；读 当前账号主绑定与依赖校验；路由 `/api/v1/bindings*`
- `students`：写 初始化与历史字段清理；读 学生实体/统计；路由 学生相关绑定/自查
- `teachers`：写 批量导入与初始化；读 教师实体；路由 `/api/v1/teachers*`
- `classes`：写 初始化与设班主任；读 班级列表/统计；路由 `/api/v1/classes*`
- `schedules`：写 初始化与设授课教师；读 学生日程/教师节次；路由 `/api/v1/schedules*`
- `attendance`：写 初始化出勤样例；读 学生今日出勤/节次出勤率；路由 仪表盘聚合
- `conduct`：写 初始化操行样例；读 学生今日操行；路由 仪表盘聚合
- `leaves`：写 初始化请假样例；读 今日/概览请假统计；路由 仪表盘聚合
- `directives`：写 初始化部门/校园指示；读 部门/校园指示列表；路由 仪表盘聚合
- `conversations`：写 新建会话/追加消息；读 用户会话/详情；路由 `/api/v1/conversations*`
- `sensitive_words`：写 管理增删/批量导入；读 加载Trie/查询；路由 `/api/v1/admin/sensitive-words*`
- `sensitive_records`：写 命中时审计记录；读 管理员查询记录；路由 `/api/v1/admin/sensitive-records`

#### 实现位置参考（按集合）
- `users`：`app/services/auth.py`、`app/api/v1/auth.py`、`init_db.py`
- `bindings`：`app/services/bindings.py`、`app/api/v1/bindings.py`、`app/api/deps.py`、`app/services/dashboard.py`
- `persons`：`app/api/v1/persons.py`、`init_db.py`
- `students`：`app/services/student_binding.py`、`app/services/dashboard.py`、`app/api/v1/students.py`、`init_db.py`
- `teachers`：`app/api/v1/teachers.py`、`app/services/dashboard.py`、`init_db.py`
- `classes`：`app/api/v1/classes.py`、`app/services/dashboard.py`、`init_db.py`
- `schedules`：`app/api/v1/schedules.py`、`app/services/dashboard.py`、`init_db.py`
- `attendance`：`app/services/dashboard.py`、`init_db.py`
- `conduct`：`app/services/dashboard.py`、`init_db.py`
- `leaves`：`app/services/dashboard.py`、`init_db.py`
- `directives`：`app/services/dashboard.py`、`init_db.py`
- `conversations`：`app/services/conversation.py`、`app/api/v1/conversations.py`、`init_db.py`
- `sensitive_words`：`app/services/sensitive_word.py`、`app/utils/sensitive_word_filter.py`、`app/api/v1/admin.py`、`init_db.py`
- `sensitive_records`：`app/services/sensitive_word.py`、`app/services/conversation.py`、`app/api/v1/admin.py`、`init_db.py`

## 敏感词过滤机制
- 使用 Trie（字典树）加载敏感词并检测文本，返回是否命中与命中的词列表
- 支持主分类与子分类，并记录严重程度（1-5，5 最严重）
- 管理员可通过导入/批量添加快速构建词库

敏感词来源与刷新机制：
- 词库存放在 MongoDB 的 `sensitive_words` 集合中。
- 应用启动时会执行 `load_sensitive_words()`，将数据库中的词库加载到内存的 Trie，用于高效匹配。
- 通过管理员接口新增/删除/批量导入敏感词后，服务会自动调用 `load_sensitive_words()` 进行“热更新”，无需重启即可生效。

运行时拦截链路：
- 接收用户消息 → 调用过滤服务检测与返回命中词与最高严重度 → 命中则写审计记录至 `sensitive_records` → 继续模型推理并合并回复 → 返回完整响应

响应示例（对话消息发送接口）：
```json
{
  "message_id": "...",
  "contains_sensitive_words": true,
  "sensitive_words_found": [
    {"word": "赌博", "category": "违法活动", "subcategory": "赌博", "severity": 3}
  ],
  "model_reply": "...",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## 部署与运维
- CORS：开发阶段允许全部来源，生产环境务必限制 `allow_origins`
- 进程与并发：开发模式使用 `--reload`；生产建议 `uvicorn` 或 `gunicorn`（多 worker）+ 进程管理（`supervisor`/`systemd`）
- 监控与审计：建议对管理员操作与敏感词命中记录进行周期性审计与归档
- 备份策略：对 `DB_NAME` 对应数据库进行定期备份，优先增量备份并校验恢复流程
- 安全基线：强随机 `SECRET_KEY`、最小权限的数据库账户、受限的网络暴露，仅在内网访问 Mongo 与 Ollama

性能与容量建议：
- Trie 加载与匹配时间随词库规模线性增长，批量导入后可观察首请求延迟
- 对话与审计记录增长较快，建议对旧记录进行归档与 TTL 管理（如为集合设置过期索引）

角色与权限等级：
- user：1（学生/员工）
- manager：2（班主任/组长/二级部门管理员）
- leader：3（中层干部/部门负责人/一级部门管理员）
- master：4（校长/集团高管/总负责人）
- administrator：5（系统管理员/运维超管；兼容历史名 `admin`）

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

4) 运行 `init_db.py` 是否会清空数据库？
- 会清空 `DB_NAME` 指定库内的所有集合（drop collection），随后再写入演示数据。仅用于开发测试，请勿在生产环境运行。
- 如需保留数据，可自行修改脚本，跳过清空步骤或仅清空指定集合；或在 `.env` 中设置不同的 `DB_NAME` 指向测试库。

---

## 许可证
本项目使用 MIT 许可证，详见 `LICENSE`。

## 贡献
欢迎提交 Issue 与 PR，共建更完善的敏感词分类与更好的对话体验。