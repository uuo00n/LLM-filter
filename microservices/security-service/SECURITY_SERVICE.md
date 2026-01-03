# Security Service 使用说明

## 1. 服务定位

Security Service 是本项目的安全分析微服务，主要能力包括：

- 基于交换机 / 防火墙 / 服务器等设备信息做 AI 安全风险分析
- 在遭受攻击时给出 AI 应急响应建议
- 生成每日安全日报
- 基于互联网最新漏洞进行风险监测与合规性评估

当前实现为 **无状态服务**：

- 不直接读写 PostgreSQL / MongoDB
- 所有分析结果仅在请求周期内计算并返回，不做持久化存储

## 2. 部署与访问入口

### 2.1 通过 Docker Compose 启动

在项目根目录执行：

```bash
cd /Users/uu/Desktop/dles_prj/llm-filter
docker-compose up -d --build security-service gateway
```

### 2.2 访问地址

- 统一网关入口（推荐）：`http://localhost:8080`
  - 安全服务 API：`/api/v1/security/*`
  - 安全服务文档：`http://localhost:8080/docs/security/`

- 直连 Security Service 容器：
  - Base URL：`http://localhost:8003`
  - API 前缀：`/api/v1/security`

## 3. 鉴权与权限控制

- 所有接口均要求携带 Auth Service 签发的 **JWT**：
  - HTTP Header：`Authorization: Bearer <token>`
- 服务内部通过 [`get_current_admin`](app/core/security.py) 校验管理员身份：
  - 仅当 `role` 为 `admin` / `administrator` / `root` 时允许访问

示例 Header：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 4. 接口一览

所有路径均在前缀 `/api/v1/security` 下，以下以 **网关地址** 为例：`http://localhost:8080`。

### 4.1 安全风险分析

- 方法：`POST`
- URL：`/api/v1/security/analysis`
- 说明：
  - 输入网络设备列表（交换机 / 防火墙 / 服务器等），由 AI 分析潜在安全隐患
  - **注意**：必须传入有效的 `devices` 列表，否则将返回空结果或错误。

请求示例：

```json
POST http://localhost:8080/api/v1/security/analysis
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "devices": [
    {
      "id": "sw-001",
      "name": "Core-Switch-A",
      "type": "switch",
      "status": "warning",
      "logs": ["Port 22 high traffic", "Packet loss detected"],
      "version": "v1.2.0"
    }
  ]
}
```

响应字段（`SecurityAnalysisResponse`）：

- `summary`: 总体安全概况
- `vulnerabilities`: 漏洞 / 风险列表
- `suggestions`: 修复建议列表
- `risk_level`: 风险等级（如 `low` / `medium` / `high` / `critical`）

### 4.2 攻击应急建议

- 方法：`POST`
- URL：`/api/v1/security/attack-advice`
- 说明：当系统已遭受攻击时，提供应急响应与缓解方案

请求示例：

```json
POST http://localhost:8080/api/v1/security/attack-advice
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "attack_type": "Brute Force Login",
  "target_device": "DB-Server-Prod",
  "severity": "high",
  "logs": "Failed login attempts from 10.0.0.10"
}
```

响应字段（`AttackAdviceResponse`）：

- `immediate_actions`: 立即执行的操作建议列表
- `analysis`: 攻击分析说明
- `mitigation_plan`: 中长期缓解与防护计划

### 4.3 安全日报

- 方法：`GET`
- URL：`/api/v1/security/report`
- 说明：生成企业安全日报，用于面向管理层的安全概览展示
- **注意**：当前实现需要接入真实数据源才能生成有效报告，否则返回空状态。

响应字段（`SecurityReportResponse`）：

- `date`: 报告日期（`YYYY-MM-DD`）
- `overall_status`: 总体安全状态
- `device_summary`: 设备运行状况摘要
- `incident_summary`: 安全事件与拦截情况摘要
- `recommendations`: 后续安全改进建议

### 4.4 风险监测与合规评估

- 方法：`GET`
- URL：`/api/v1/security/monitor`
- 说明：基于互联网最新漏洞信息，评估当前企业的合规风险
- **注意**：需要配置或接入外部漏洞数据库，否则返回空列表。

响应字段（`RiskMonitorResponse`）：

- `detected_vulnerabilities`: 识别到的漏洞列表
- `compliance_risks`: 合规风险点列表
- `ai_assessment`: AI 对整体风险的评估说明

### 4.5 安全新闻 RSS 订阅

- 方法：`GET`
- URL：`/api/v1/security/rss/news`
- 说明：获取来自天融信、360 CERT、绿盟等安全厂商的最新 RSS 安全资讯。

响应字段（`RSSFeedResponse`）：

- `items`: 新闻列表，包含标题、链接、摘要、发布时间和来源。

## 5. Dify 集成与异常处理

服务内部通过 Dify 完成大部分安全分析逻辑：

- Dify 调用配置在 [config.py](app/core/config.py)：
  - `DIFY_API_URL`
  - `DIFY_API_KEY`
- 请求由 [`SecurityService._call_llm`](app/services/analysis.py) 统一发起
- **智能体 Prompt 配置**：请参考 [DIFY_PROMPT.md](DIFY_PROMPT.md) 文档，在 Dify 平台配置对应的 System Prompt 和变量。

当 Dify 不可用（网络异常 / 超时 / 抛错）时：

- 服务将记录错误日志
- 抛出异常供上层处理或返回 HTTP 500 错误
- **不再提供 Mock 数据降级**，以确保运维人员能及时感知服务状态异常。

## 6. 数据存储与状态

当前版本的 Security Service：

- 不写入任何数据库（PostgreSQL / MongoDB）
- 不记录历史分析结果或报告
- 所有分析基于：
  - 请求中传入的设备数据
  - 实时从 Dify 获取的分析结果

后续如果需要：

- 可以将分析结果落库到 PostgreSQL 或 MongoDB
- 典型扩展：
  - 安全日报历史查询
  - 风险趋势分析
  - 设备安全基线与偏离检测

## 7. 快速调试示例（curl）

确保容器已启动后，可以在宿主机直接运行：

```bash
# 1. 使用管理员 Token 调用安全分析（通过网关）
# 注意：请确保传入真实的设备数据
curl -X POST "http://localhost:8080/api/v1/security/analysis" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"devices": [{"id": "test-1", "name": "Test-Device", "type": "server", "status": "active"}]}'

# 2. 直接访问文档（网关统一入口）
open "http://localhost:8080/docs/security/"
```
