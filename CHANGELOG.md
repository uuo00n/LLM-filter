# LLM Filter 更新日志

## [Unreleased] — 2025-12-08

- 新增
  - 完善 API 文档与错误响应，统一 `summary/description/responses`（对话、学生、管理员、绑定、班级、课表、人物、仪表盘、认证）。
  - 自定义 Swagger UI 通过 CDN 加载静态资源，提升可访问性。
  - 添加 `APP_BASE_URL` 配置，在启动时打印文档地址。
- 修复
  - 敏感词处理逻辑兼容新旧版本，修复记录中用户/对话 ID 类型转换问题。
  - 仪表盘校园总览接口角色等级要求由 5 调整为 4。
  - 考勤统计缺失课程 ID 等问题修复。
- 重构
  - 升级并适配 Pydantic v2，更新模型与设置读取方式（`pydantic-settings`）。
  - 统一鉴权依赖与权限等级校验；账户与人物实体分离，绑定机制统一。
  - 敏感词记录功能重构，增加详细敏感词信息与审计能力；CORS 允许源与凭证动态配置。
- 文档
  - 更新 README，补充实体化模型、接口说明、Windows PowerShell 快速启动指南与许可证信息。
  - 在 OpenAPI 中增加 `version`、`contact`（邮箱：`huangjunbo1107@outlook.com`）、`license` 元信息。
- 运维与杂项
  - 更新 OLLAMA 模型配置（示例：`deepseek-r1:14b`），清理编译缓存与完善 `.gitignore`。

### 关联提交（摘要）
- 10e59f3 feat: 完善API文档和错误响应
- 2724a77 feat(配置): 添加APP_BASE_URL配置并显示API文档链接
- cbd3da7 refactor(models): 更新Pydantic模型配置以兼容v2版本
- 4711122 docs: 更新README文档内容与格式
- 7a1720e fix(conversation): 更新敏感词处理逻辑以兼容新旧版本
- adff7ae feat(core): 添加CORS和GitHub相关配置项
- 789fdcb feat(api): 对话路由统一响应模型，新增删除接口；列表负载优化
- 35d99c7 fix(dashboard): 将校园总览接口的角色等级要求从5级降至4级
- 5dbcb42 feat: 重构用户与实体模型，实现账户与人物分离
- 05ab73d feat(学生绑定): 实现用户与学生绑定功能及接口

## 1.0.0 — 2025-10-31

- 项目初始化：LLM 过滤系统后端（FastAPI + MongoDB + Ollama）。
- 敏感词分类与严重程度管理、管理员操作与审计追踪基础能力。
- README 与 MIT 许可证添加，基础安装与运行说明。

