## 目标
- 用中文完善 README，对当前架构、鉴权口径、数据模型与主要接口进行系统化说明，便于快速上手与联调。

## README 结构
1) 项目简介
- 简述：LLM 过滤系统后端；统一角色等级与实体化数据模型；支持教育/企业版运行模式。

2) 技术栈
- FastAPI、Motor/PyMongo、Pydantic v2、Uvicorn、HTTPX；MongoDB

3) 运行与端口
- 开发启动：`uvicorn app.main:app --reload --port 8000`
- 文档：`http://127.0.0.1:8000/docs`

4) 环境变量
- 核心：`MONGODB_URL/DB_NAME/APP_MODE/SECRET_KEY/ALGORITHM/ACCESS_TOKEN_EXPIRE_MINUTES`
- 外部：`OLLAMA_BASE_URL/OLLAMA_MODEL`
- 初始密码：`ADMIN_EDU_PASSWORD/USER_EDU_PASSWORD/MANAGER_EDU_PASSWORD/LEADER_EDU_PASSWORD/MASTER_EDU_PASSWORD` 与企业版对应变量

5) 初始化数据库
- 命令：`python init_db.py`
- 内容：创建用户、敏感词、对话；创建并填充 students/classes/schedules/attendance/conduct/leaves/directives；生成 persons/teachers/bindings 并清理旧字段与索引

6) 鉴权口径
- 角色等级：1 学生、2 班主任、3 中层、4 校级、5 管理员
- 版别依赖：`require_edition_for_mode()`
- 实体绑定依赖：`require_binding(student|teacher)`；登录载荷含 `person_id/person_type/bound_primary`

7) 数据模型（Mongo 集合）
- `users`（账号）；`persons`（人物）；`students`/`teachers`（实体）；`bindings`（绑定）
- 班级：`classes`（`head_teacher_person_id`）；课表：`schedules`（共享节次，`teacher_person_id`）
- 出勤与行为：`attendance/leaves/conduct`；指示：`directives`
- 敏感词与审计：`sensitive_words/sensitive_records`；对话：`conversations`

8) 主要接口
- 认证：`POST /auth/register`、`POST /auth/login`
- 仪表盘：学生/班主任/中层/校级（`/dashboard/...`）
- 学生：`/students/me`、绑定：`POST/DELETE /bindings`、`GET /bindings/me`
- 人员：`POST /persons/bulk`、`GET /persons`
- 教师：`POST /teachers/bulk`、`GET /teachers`
- 班级：`PUT /classes/{class_id}/head-teacher`、`GET /classes`
- 课表：`PUT /schedules/assign-teacher`、`GET /schedules`

9) 快速演示
- 示例账号与密码（教育版）：`admin/admin123`、`user/user123`、`manager_edu/manager123`、`leader_edu/leader123`、`master_edu/master123`
- 绑定流程：登录→查询/创建绑定→访问仪表盘

10) 注意事项
- ObjectId 序列化：接口返回不包含原始 `ObjectId`；如需返回 `_id`，统一转换为字符串
- 索引：`person_id` 稀疏唯一；`head_teacher_person_id`/`teacher_person_id` 索引、课表组合索引、出勤组合索引

## 交付方式
- 更新根目录 `README.md` 文件内容为以上结构
- 保持内容简洁、示例充分，与 `/docs` 文档一致

确认后我将直接更新 README.md 并进行一次端到端核对（初始化与接口文档一致性）。