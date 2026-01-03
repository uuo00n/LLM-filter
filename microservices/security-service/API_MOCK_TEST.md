# Security Service API 测试与假数据示例

本文件用于说明如何通过 HTTP API（经网关或直连服务）调用 Security Service，并使用一组统一的假数据进行联调和回归测试。

> 注意：这些假数据仅用于测试，生产环境请接入真实监控和日志数据。

---

## 1. 环境与前提条件

- 网关地址（推荐）：`http://localhost:8080`
- Security Service API 前缀：`/api/v1/security`
- 所有接口均需要携带管理员 JWT：
  - Header：`Authorization: Bearer <admin_token>`

在以下示例中，请将 `<admin_token>` 替换为实际从 Auth Service 获取的 token。

---

## 2. 接口一览

- `POST /api/v1/security/analysis` —— 安全风险分析
- `POST /api/v1/security/attack-advice` —— 攻击应急建议
- `GET  /api/v1/security/report` —— 安全日报
- `GET  /api/v1/security/monitor` —— 风险监测与合规评估

---

## 3. 安全风险分析（/analysis）测试示例

### 3.1 请求说明

- 方法：`POST`
- URL：`http://localhost:8080/api/v1/security/analysis`
- 用途：基于设备信息列表做 AI 风险分析。

### 3.2 测试请求体（假数据）

```json
{
  "devices": [
    {
      "id": "sw-001",
      "name": "Core-Switch-A",
      "type": "switch",
      "status": "warning",
      "version": "v1.2.0",
      "logs": [
        "Port 22 high traffic",
        "Packet loss detected"
      ]
    },
    {
      "id": "fw-001",
      "name": "Edge-Firewall",
      "type": "firewall",
      "status": "active",
      "version": "v2.1.patch3",
      "logs": [
        "Denied 1000+ requests from IP 192.168.1.50"
      ]
    }
  ]
}
```

### 3.3 curl 示例

```bash
curl -X POST "http://localhost:8080/api/v1/security/analysis" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "id": "sw-001",
        "name": "Core-Switch-A",
        "type": "switch",
        "status": "warning",
        "version": "v1.2.0",
        "logs": ["Port 22 high traffic", "Packet loss detected"]
      },
      {
        "id": "fw-001",
        "name": "Edge-Firewall",
        "type": "firewall",
        "status": "active",
        "version": "v2.1.patch3",
        "logs": ["Denied 1000+ requests from IP 192.168.1.50"]
      }
    ]
  }'
```

### 3.4 期望响应结构

服务端返回 JSON 结构符合 `SecurityAnalysisResponse`：

```json
{
  "summary": "string",
  "vulnerabilities": ["string"],
  "suggestions": ["string"],
  "risk_level": "string"
}
```

---

## 4. 攻击应急建议（/attack-advice）测试示例

### 4.1 请求说明

- 方法：`POST`
- URL：`http://localhost:8080/api/v1/security/attack-advice`
- 用途：当系统已遭受攻击或疑似攻击时，获取应急响应方案。

### 4.2 测试请求体（假数据）

```json
{
  "attack_type": "Brute Force Login",
  "target_device": "DB-Server-Prod",
  "severity": "high",
  "logs": "Failed login attempts from 10.0.0.10"
}
```

### 4.3 curl 示例

```bash
curl -X POST "http://localhost:8080/api/v1/security/attack-advice" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "attack_type": "Brute Force Login",
    "target_device": "DB-Server-Prod",
    "severity": "high",
    "logs": "Failed login attempts from 10.0.0.10"
  }'
```

### 4.4 期望响应结构

```json
{
  "immediate_actions": ["string"],
  "analysis": "string",
  "mitigation_plan": "string"
}
```

---

## 5. 安全日报（/report）测试示例

### 5.1 请求说明

- 方法：`GET`
- URL：`http://localhost:8080/api/v1/security/report`
- 用途：生成面向管理层的每日安全概览。

### 5.2 curl 示例

```bash
curl -X GET "http://localhost:8080/api/v1/security/report" \
  -H "Authorization: Bearer <admin_token>"
```

> 当前实现中，后端会构造简单的统计信息传给 Dify。实际环境应接入真实监控数据。

### 5.3 期望响应结构

```json
{
  "date": "string",
  "overall_status": "string",
  "device_summary": "string",
  "incident_summary": "string",
  "recommendations": "string"
}
```

---

## 6. 风险监测与合规评估（/monitor）测试示例

### 6.1 请求说明

- 方法：`GET`
- URL：`http://localhost:8080/api/v1/security/monitor`
- 用途：基于给定的漏洞信息进行整体风险与合规评估。

> 当前代码中 `context_data` 为空数组时，智能体可以根据默认经验或空数据做基线评估。也可以在后续版本中从漏洞库/配置注入具体列表。

### 6.2 curl 示例

```bash
curl -X GET "http://localhost:8080/api/v1/security/monitor" \
  -H "Authorization: Bearer <admin_token>"
```

### 6.3 期望响应结构

```json
{
  "detected_vulnerabilities": ["string"],
  "compliance_risks": ["string"],
  "ai_assessment": "string"
}
```

---

## 7. 测试建议

- 在联调阶段，可以先固定一组假数据（如本文件中的示例），确保：
  - Dify 智能体返回的 JSON 结构稳定且字段完整；
  - Security Service 能正确解析并返回给前端。
- 回归测试时：
  - 建议将这些请求录入到自动化测试脚本中（如 pytest + httpx/requests），
  - 对响应结构做 Schema 校验，避免后续修改提示词或模型配置导致输出结构破坏。