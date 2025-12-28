# 校园 AI 智能助手：后端安全防护深度解析（基于本项目实现）
演讲稿与技术指南（Markdown）

> 说明：本文所有机制与代码片段均来自当前项目 `llm-filter` 的真实实现（网关 Nginx + Go Auth Service + Java Edu Service + Python LLM Service）。

---

## 开场白：为什么 AI 时代的后端安全是“最后裁决者”？

**演讲参考：**  
“各位好！前端安全更像是‘门口保安’，而后端安全才是‘教务系统的总闸门’：身份、权限、数据、审计、合规，都必须在服务端形成闭环。  
在我们的校园 AI 智能助手项目里，后端并不是一个单体应用，而是由 **网关（Nginx）+ 三个微服务（Auth/Edu/LLM）**组成。今天我会沿着一条请求从入口到模型的路径，把我们的后端安全‘五道防线’讲清楚。”

---

## 先给大家一张地图：项目后端安全链路总览

- **网关层（Nginx）**：统一入口与路由分发  
  - 配置：`gateway/nginx.conf`
- **认证层（Auth Service / Go + Gin）**：登录、注册、绑定关系、JWT 签发与校验  
  - 入口：`microservices/auth-service/main.go`  
  - JWT：`microservices/auth-service/pkg/utils/jwt.go`  
  - 中间件：`microservices/auth-service/pkg/middleware/auth.go`
- **教务层（Edu Service / Java + Spring）**：教务数据接口，JWT 过滤器注入 UserContext  
  - Filter：`microservices/edu-service/.../security/JwtAuthenticationFilter.java`  
  - 注册：`microservices/edu-service/.../EduServiceApplication.java`
- **LLM 层（LLM Service / Python + FastAPI）**：对话、敏感词库、敏感审计、模型调用  
  - 鉴权依赖：`microservices/llm-service/app/api/deps.py`  
  - 敏感词过滤：`microservices/llm-service/app/utils/sensitive_word_filter.py`  
  - 对话写入与审计：`microservices/llm-service/app/services/conversation.py`

---

## 第一章：守门人——网关统一入口与服务边界隔离（Gateway）

### 设计哲学
**安全的第一原则：入口要收敛。**  
我们将所有外部访问统一打到网关，由网关做路由分发，让每个微服务只暴露必要的端口与路径（在容器网络内通信）。

### 核心实现（`gateway/nginx.conf`）
```nginx
# Auth Service 路由：认证与绑定走 auth-service
location /api/v1/auth {
    proxy_pass http://auth_service/api/v1/auth;
    proxy_set_header Host $host;        # 透传 Host 便于服务端识别来源
    proxy_set_header X-Real-IP $remote_addr; # 透传真实 IP 便于审计
}

# LLM Service 路由（兜底）：其余请求默认转发到 llm-service
location / {
    proxy_pass http://llm_service/;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 链路追踪
}
```

**演讲参考：**  
“我们把微服务当成不同的‘功能分区’：认证归认证、教务归教务、对话归对话。统一入口的好处是：策略集中、边界清晰、后续要加限流/黑白名单也只需要改一个地方。”

---

## 第二章：身份钢印——JWT 签发、校验与跨服务一致性（Auth / Edu / LLM 三方对齐）

### 设计哲学
- **身份要可验证**：不能只“信任前端传来的 user_id / role”
- **权限要可携带**：让每个服务都能在本地完成快速决策
- **跨语言一致**：Go 签发、Java/Python 校验必须字段一致、密钥一致

### 1）Auth Service：JWT 里写入角色与绑定信息（`pkg/utils/jwt.go`）
```go
claims := jwt.MapClaims{
  "sub": userID,                 // 用户唯一标识（下游用它做“谁发起的”）
  "name": username,              // 用户名展示/审计
  "role": role,                  // 角色（admin/administrator/user 等）
  "role_level": roleLevel,       // 角色等级（用于更细粒度的授权）
  "edition": edition,            // 版别（edu/biz）
  "person_id": personID,         // 绑定的业务身份（学生/教师/人员）
  "person_type": personType,     // 绑定类型（下游据此做数据边界）
  "exp": time.Now().Add(24*time.Hour).Unix(), // 过期时间：避免长期滥用
}
```

### 2）Edu Service：过滤器统一校验 Authorization，并注入 UserContext（`JwtAuthenticationFilter.java`）
```java
String authHeader = httpRequest.getHeader("Authorization");
if (StringUtils.hasText(authHeader) && authHeader.startsWith("Bearer ")) {
  String token = authHeader.substring(7); // 提取 Bearer Token
  Claims claims = Jwts.parserBuilder()
      .setSigningKey(key)                 // 使用 jwt.secret 验签
      .build()
      .parseClaimsJws(token)
      .getBody();

  String role = claims.get("role", String.class);       // 角色
  String personId = claims.get("person_id", String.class); // 绑定身份
  UserContextHolder.setContext(UserContext.builder()
      .role(role).personId(personId).build());          // 注入线程上下文
}
```

### 3）LLM Service：FastAPI 依赖中本地验签，不再回调 Auth（`app/api/deps.py`）
```py
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
user_id = payload.get("sub")     # 与 Go 端保持一致：sub
role = payload.get("role")       # 角色用于管理员接口保护

if current_user.get("role") not in {"admin", "administrator"}:
    raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
```

**演讲参考：**  
“我们用 JWT 做了一件关键的事：把‘身份、角色、绑定关系、版别’这四类安全上下文变成可验证的钢印。这样 Java 的教务服务、Python 的对话服务都能本地做快速决策，不需要每次再回调认证中心，既安全又高性能。”

---

## 第三章：权限隔离——绑定关系驱动的“数据边界”（从 token 到数据行）

### 设计哲学
校园系统的权限不只是“你是不是管理员”，更常见的是：
- **你是不是这名学生本人**
- **你是不是这位老师本人**
- **你有没有绑定到某个 person_id**

### 1）Auth Service：绑定接口必须先过认证（`auth-service/main.go`）
```go
bindingsGroup := v1.Group("/bindings")
bindingsGroup.Use(middleware.AuthMiddleware()) // 先验证 JWT，再允许绑定操作
{
  bindingsGroup.POST("", bindingHandler.Bind)
  bindingsGroup.GET("/me", bindingHandler.Me)
}
```

### 2）Edu Service：业务层用 person_id 做“学生/教师边界”（`DashboardServiceImpl.java`）
```java
String personId = user.getPersonId();
if (personId == null) {
  throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "未绑定学生");
}

Student student = studentRepository.findByPersonId(personId)
  .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "未找到学生档案"));
```

### 3）LLM Service：Mongo 查询强制带 user_id，防止横向越权（`services/conversation.py`）
```py
conversation = await db.db.conversations.find_one({
  "_id": ObjectId(conversation_id),
  "user_id": user_id,  # 关键：必须属于当前用户
})
if not conversation:
  return None
```

**演讲参考：**  
“在校园场景里，最危险的往往不是‘能不能登录’，而是‘能不能看见不属于自己的数据’。我们用 `person_id` 绑定把学生/教师身份落实到 token 上，再用 `user_id` 归属校验把每次查询锁进自己的数据范围。”

---

## 第四章：内容护盾——敏感词过滤 + 智能体二次审核 + 审计留痕（LLM Service）

### 设计哲学
AI 内容不可预测，所以我们把后端对话链路当成“高危管道”来做：
- **先本地过滤**（成本低、速度快）
- **再智能体审核**（更强但更贵）
- **命中即拒答，并落审计**（可追责、可复盘）

### Dify Agent：把“内容安全判定”做成一台无状态机器

**演讲参考：**  
“这里我们引入了 Dify Agent，但我们不把它当聊天机器人，而是当一台‘判定机器’：只负责审核，不负责对话。它的工作方式非常硬核：优先做知识库命中，其次做语义风险评估，最终只返回一个标准 JSON，做到可自动化、可审计、可接入任何链路。”

我们的 Agent 提示词（系统约束）强调四个关键点：
- **知识库驱动 + 无状态**：每次请求独立判定，不记忆用户上下文，避免被“洗脑”
- **命中即阻断**：敏感实体/变体一旦命中，直接给出 BLOCK 结果，不进入后续推理
- **反指令注入**：任何试图改规则的输入，直接归类为“违法活动”
- **唯一输出格式**：严格只输出 JSON（`safe/reason/suggestion`），便于后端统一处理与落库

在我们的代码里，Dify Agent 的落点也非常明确：
- **配置来自容器环境变量**：`DIFY_API_URL / DIFY_API_KEY / DIFY_RESPONSE_MODE`（见 `docker-compose.yml` 与 `app/core/config.py`）
- **调用封装在统一服务层**：`app/services/dify.py` 的 `check_content_safety()`
- **执行时机是“本地词库放行之后”**：在 `app/services/conversation.py` 里，只有当 Trie 未命中敏感词，才会触发 Dify 二次审核

### 1）本地敏感词 Trie 匹配（`utils/sensitive_word_filter.py`）
```py
# 关键点：敏感词从 Mongo 加载到 Trie，检查时只做本地匹配
cursor = db.db.sensitive_words.find({})
async for document in cursor:
  word = document.get("word", "")
  if word:
    self._add_to_trie(word, word_info)

# 检测：逐字符向前匹配，命中即记录（并计算最高严重程度）
text_lower = text.lower()
```

### 2）敏感词词库：MongoDB + 管理接口 + 启动加载

- 词库数据落在 MongoDB 的 `sensitive_words` 集合中，并在 LLM 服务启动时加载为 Trie（`app/main.py` 中 `load_sensitive_words()`）
- 管理侧提供敏感词与分类的增删改查与批量导入（`app/api/v1/admin.py`，依赖 `get_current_admin_user` 做管理员权限保护）

### 3）对话写入前的“二级过滤”，命中则拒答 + 记录审计（`services/conversation.py`）
```py
check_result = sensitive_word_filter.check_text(content)   # 本地敏感词命中
if not check_result["contains_sensitive_words"]:
    dify_result = await dify_service.check_content_safety(content, user_id) # 智能体审核

if contains_sensitive:
    await db.db.sensitive_records.insert_one({             # 落审计（可追责）
      "user_id": user_id,
      "message_content": content,
      "sensitive_words_found": detailed_words,
      "highest_severity": highest,
    })
    return {"assistant_response": "当前问题暂无法回答。"}     # 统一拒答出口
```

**演讲参考：**  
“我们不是让 AI ‘自由发挥’，而是把它放进一条带阀门的安全管道：先用本地敏感词把明显违规的拦住，再用智能体对隐蔽风险做二次判断，一旦命中就拒答并留下审计记录。”

---

## 第五章：工程化安全——接口暴露面、文档入口与运行模式隔离（Edu / LLM）

### 设计哲学
- **暴露面越小越安全**：能不公开就不公开
- **文档与健康检查要可控**：该跳过就跳过，但不能把敏感接口也放开
- **运行模式要隔离**：教育版/企业版不应混跑导致权限穿透

### 1）Edu Service：公开路径白名单（Swagger/Health 放行，其它都要 token）
`JwtAuthenticationFilter.java` 中 `isPublicPath()` 明确放行：
- `/swagger-ui`
- `/v3/api-docs`
- `/api/v1/edu/health`

### 2）LLM Service：版别运行模式依赖（`app/api/deps.py`）
```py
mode = (settings.APP_MODE or "edu").lower()  # 运行模式：edu/biz
if mode in {"edu", "biz"}:
    user_edition = (current_user.get("edition") or "").lower()
    if user_edition != mode:
        raise HTTPException(status_code=403, detail="当前模式无权访问")
```

**演讲参考：**  
“安全工程化的关键是：把‘约束’写进框架层。我们把版别隔离做成了路由依赖，让错误配置和越权访问在最靠前的位置就失败。”

---

## 当前项目“已实现”的后端安全点（清单式总结）

- **统一入口与服务边界**：网关统一路由分发（`gateway/nginx.conf`）
- **JWT 身份闭环**：Auth 签发，Edu/LLM 本地验签（Go/Java/Python 对齐）
- **绑定关系驱动的数据边界**：token 携带 `person_id/person_type`，教务接口基于绑定读取
- **横向越权防护**：LLM 对话 Mongo 查询强制带 `user_id`
- **内容合规链路**：敏感词 Trie + 智能体审核 + `sensitive_records` 审计落库
- **版别隔离**：LLM 层 `APP_MODE` 与 token `edition` 做强校验

## 结语：防御在后端，体验在前端

**演讲参考：**  
“我们这套系统的安全，不靠某一个‘神奇中间件’，而是靠从网关到鉴权、从绑定到数据边界、从内容审核到审计留痕的一条链路闭环。  
对用户来说，体验依旧是‘顺滑可用’；但对系统来说，每一次请求都在规则之内，每一条敏感行为都能追溯。谢谢大家！”

---

## 文档信息
- 文档类型：技术演讲稿与实现指南  
- 主题：校园 AI 智能助手后端安全防护（基于 llm-filter 项目）  
- 版本：项目对齐版  
- 日期：2025年12月  
