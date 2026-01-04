# 更新日志（CHANGELOG）

本文件根据 `main` 分支的 git 提交历史整理（共 53 条）。当前仓库未打版本标签（tag），因此按日期归档；后续如引入版本号，可将日期段迁移为版本段。

仓库地址：https://github.com/uuo00n/LLM-filter

## 2026-01-04

### 新增

- 新增 **Security Service** 微服务，提供安全分析与风险监控能力。
- Security Service: 支持 MongoDB 异步持久化分析与攻击建议记录。
- Security Service: 提供历史记录查询接口，支持时间范围筛选。
- 文档：更新 DEVELOPMENT.md, README.md, SPEAK.md, 白皮书等文档以反映最新架构。

## 2025-12-28

### 新增

- Dify 智能体内容安全检查（[`15c33bc`](https://github.com/uuo00n/LLM-filter/commit/15c33bc)）

### 文档

- 更新项目文档结构和内容（[`6a87f73`](https://github.com/uuo00n/LLM-filter/commit/6a87f73)）

## 2025-12-27

### 新增

- 重构项目为微服务架构并添加教育服务模块（[`6cf8357`](https://github.com/uuo00n/LLM-filter/commit/6cf8357)）
- 教育服务实现仪表盘功能并完成迁移（[`40f9fb5`](https://github.com/uuo00n/LLM-filter/commit/40f9fb5)）

## 2025-12-14

### 文档

- 添加 LLM-Filter 技术白皮书初稿（[`708db1b`](https://github.com/uuo00n/LLM-filter/commit/708db1b)）

### 杂项

- 清理虚拟环境中的旧文件和依赖项（[`96c5056`](https://github.com/uuo00n/LLM-filter/commit/96c5056)）

## 2025-12-13

### 新增

- 学生周课表查询功能（仪表盘）（[`e13c147`](https://github.com/uuo00n/LLM-filter/commit/e13c147)）
- 教师周课表查询功能（仪表盘）（[`7133e3a`](https://github.com/uuo00n/LLM-filter/commit/7133e3a)）

### 修复

- 修复默认用户关联学生实体缺失导致 `/students/me` 404（[`0d0589b`](https://github.com/uuo00n/LLM-filter/commit/0d0589b)）
- 确保 `teacher_person_id` 与 `created_at` 的格式正确（[`befb276`](https://github.com/uuo00n/LLM-filter/commit/befb276)）

### 文档

- 更新 CHANGELOG 与 README 以反映最新更改（[`f4b6195`](https://github.com/uuo00n/LLM-filter/commit/f4b6195)）

### 杂项

- 更新 `.env` 中的数据库配置（[`6d17b88`](https://github.com/uuo00n/LLM-filter/commit/6d17b88)）

## 2025-12-08

### 新增

- 完善 API 文档与错误响应（[`10e59f3`](https://github.com/uuo00n/LLM-filter/commit/10e59f3)）
- 添加 `APP_BASE_URL` 配置并启动时输出文档链接（[`2724a77`](https://github.com/uuo00n/LLM-filter/commit/2724a77)）

### 修复

- 更新敏感词处理逻辑以兼容新旧版本（[`7a1720e`](https://github.com/uuo00n/LLM-filter/commit/7a1720e)）

### 重构

- 更新 Pydantic 模型配置以兼容 v2（[`cbd3da7`](https://github.com/uuo00n/LLM-filter/commit/cbd3da7)）

### 文档

- 更新 README 文档内容与格式（[`4711122`](https://github.com/uuo00n/LLM-filter/commit/4711122)）
- 添加项目更新日志文件记录版本变更（[`76324c6`](https://github.com/uuo00n/LLM-filter/commit/76324c6)）

### 杂项

- 清理过时文档文件（[`2b45781`](https://github.com/uuo00n/LLM-filter/commit/2b45781)）
- 清理 Python 编译缓存文件（[`6290fb1`](https://github.com/uuo00n/LLM-filter/commit/6290fb1)）
- 添加 Python 项目通用 `.gitignore`（[`f014fc6`](https://github.com/uuo00n/LLM-filter/commit/f014fc6)）

## 2025-12-04

### 新增

- 添加 CORS 与 GitHub 相关配置项（[`adff7ae`](https://github.com/uuo00n/LLM-filter/commit/adff7ae)）

## 2025-11-30

### 新增

- 对话：统一 ID 与标题、敏感词结构化返回、新增删除接口与 CORS 支持（[`4c2e734`](https://github.com/uuo00n/LLM-filter/commit/4c2e734)）
- 对话：列表与详情统一 ID/标题，新增删除对话服务（[`52ef3e5`](https://github.com/uuo00n/LLM-filter/commit/52ef3e5)）
- API：对话路由统一响应模型，新增删除接口；列表负载优化（[`789fdcb`](https://github.com/uuo00n/LLM-filter/commit/789fdcb)）

### 合并

- 合并 PR #13：conversation unify/title/delete/cors（[`28ce2b7`](https://github.com/uuo00n/LLM-filter/commit/28ce2b7)）

## 2025-11-19

### 文档

- 添加 Windows PowerShell 快速启动指南（[`aea76f6`](https://github.com/uuo00n/LLM-filter/commit/aea76f6)）

## 2025-11-18

### 修复

- 修复敏感词记录中用户ID与对话ID的类型转换问题（[`b5ca224`](https://github.com/uuo00n/LLM-filter/commit/b5ca224)）

### 重构

- 重构敏感词记录：包含详细敏感词信息（[`b5ca224`](https://github.com/uuo00n/LLM-filter/commit/b5ca224)）
- CORS：根据配置动态设置允许的源与凭证（[`b5ca224`](https://github.com/uuo00n/LLM-filter/commit/b5ca224)）

### 风格

- 移除不必要的注释与空行（[`b5ca224`](https://github.com/uuo00n/LLM-filter/commit/b5ca224)）

## 2025-11-17

### 新增

- 自定义 Swagger UI 使用 CDN 加载静态资源（[`928e789`](https://github.com/uuo00n/LLM-filter/commit/928e789)）

### 文档

- 更新 README 以提供更全面的系统文档（[`59d1878`](https://github.com/uuo00n/LLM-filter/commit/59d1878)）

### 杂项

- 更新数据库配置和依赖项（[`a721cb0`](https://github.com/uuo00n/LLM-filter/commit/a721cb0)）

## 2025-11-14

### 新增

- 添加学校业务数据初始化能力（[`6bc71b9`](https://github.com/uuo00n/LLM-filter/commit/6bc71b9)）
- 添加后端仪表盘功能模块（[`65250db`](https://github.com/uuo00n/LLM-filter/commit/65250db)）
- 实现用户与学生绑定功能及接口（[`05ab73d`](https://github.com/uuo00n/LLM-filter/commit/05ab73d)）
- 重构用户与实体模型：账户与人物分离（[`5dbcb42`](https://github.com/uuo00n/LLM-filter/commit/5dbcb42)）
- 统一鉴权方案并清理冗余字段（[`b5ec343`](https://github.com/uuo00n/LLM-filter/commit/b5ec343)）
- 人员统计：按类型统计并返回分项计数（[`fddd97e`](https://github.com/uuo00n/LLM-filter/commit/fddd97e)）
- 为多个 API 端点添加响应模型定义（[`d149e42`](https://github.com/uuo00n/LLM-filter/commit/d149e42)）

### 修复

- 修复考勤统计中缺少课程ID的问题（[`7d00ec6`](https://github.com/uuo00n/LLM-filter/commit/7d00ec6)）
- 将绑定数据中的 `_id` 字段转换为字符串（[`0cea2c6`](https://github.com/uuo00n/LLM-filter/commit/0cea2c6)）
- 将校园总览接口角色等级要求从 5 级降至 4 级（[`35d99c7`](https://github.com/uuo00n/LLM-filter/commit/35d99c7)）

### 文档

- README：补充实体化模型与接口文档说明（[`f1739a6`](https://github.com/uuo00n/LLM-filter/commit/f1739a6)）

## 2025-11-10

### 新增

- 迁移 BaseSettings 至 pydantic-settings 并新增 `APP_MODE`（[`8ba714b`](https://github.com/uuo00n/LLM-filter/commit/8ba714b)）

### 重构

- 移除后端仪表盘接口，改由前端实现（[`b51127a`](https://github.com/uuo00n/LLM-filter/commit/b51127a)）

### 文档

- README：补充重要说明与细节（[`d21ebdb`](https://github.com/uuo00n/LLM-filter/commit/d21ebdb)）

## 2025-11-05

### 杂项

- 更新 Ollama 配置与 Python 虚拟环境文件（[`24e31fa`](https://github.com/uuo00n/LLM-filter/commit/24e31fa)）
- 更新 `OLLAMA_MODEL` 为 `deepseek-r1:14b`（[`0bbc809`](https://github.com/uuo00n/LLM-filter/commit/0bbc809)）

## 2025-11-04

### 文档

- 更新 README 文档内容与格式（[`9fadbc5`](https://github.com/uuo00n/LLM-filter/commit/9fadbc5)）

## 2025-10-31

### 新增

- 初始化 LLM 过滤系统项目（[`3cc8824`](https://github.com/uuo00n/LLM-filter/commit/3cc8824)）
- 增强敏感词分类与严重程度管理（[`5a2cce0`](https://github.com/uuo00n/LLM-filter/commit/5a2cce0)）

### 文档

- 添加项目 README（系统概述与安装说明）（[`5b8eb45`](https://github.com/uuo00n/LLM-filter/commit/5b8eb45)）
- 更新 README：许可证与联系方式（[`2f09184`](https://github.com/uuo00n/LLM-filter/commit/2f09184)）
- 添加 MIT License 文件（[`2612a04`](https://github.com/uuo00n/LLM-filter/commit/2612a04)）

