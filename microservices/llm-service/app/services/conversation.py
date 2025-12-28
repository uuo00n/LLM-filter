from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import db
from app.services.ollama import generate_response
from app.utils.sensitive_word_filter import sensitive_word_filter
from app.services.dify import dify_service

async def create_conversation(user_id: str) -> str:
    """创建新对话
    用途：为指定用户创建一个新的对话，初始化空消息与默认标题。
    入参：
    - user_id: 当前用户的字符串 ID
    返回：
    - 新建对话的字符串 ID
    """
    conversation = {
        "user_id": user_id,
        "title": f"新会话 {datetime.now().strftime('%m-%d %H:%M')}",
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = await db.db.conversations.insert_one(conversation)
    return str(result.inserted_id)

async def get_conversation(conversation_id: str, user_id: str) -> Optional[Dict]:
    """获取单个对话
    用途：根据对话 ID 和用户 ID 获取该用户的单个对话，并规范返回字段。
    入参：
    - conversation_id: 对话ID
    - user_id: 用户ID
    返回：
    - 对话字典（含 id/_id/title/messages 等）或 None
    """
    conversation = await db.db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": user_id
    })
    
    if not conversation:
        return None

    # 统一 ID 字段与用户 ID 字符串化
    conversation["id"] = str(conversation["_id"])
    conversation["_id"] = str(conversation["_id"])  # 兼容旧前端
    conversation["user_id"] = str(conversation["user_id"])    
    # 标题兜底
    if not conversation.get("title"):
        conversation["title"] = f"新会话 {conversation.get('created_at', datetime.now()).strftime('%m-%d %H:%M')}"

    # 将消息中的敏感词字符串列表转换为结构化对象
    messages: List[Dict[str, Any]] = conversation.get("messages", [])
    # 汇总所有可能的敏感词
    all_words: List[str] = []
    for m in messages:
        sw = m.get("sensitive_words_found", [])
        if sw and isinstance(sw, list) and (len(sw) == 0 or isinstance(sw[0], str)):
            all_words.extend([w for w in sw if isinstance(w, str)])
    unique_words = list(set(all_words))

    word_detail_map: Dict[str, Dict[str, Any]] = {}
    if unique_words:
        cursor = db.db.sensitive_words.find({"word": {"$in": unique_words}})
        async for doc in cursor:
            word_detail_map[doc.get("word")] = {
                "word": doc.get("word"),
                "category": doc.get("category"),
                "subcategory": doc.get("subcategory"),
                "severity": doc.get("severity", 1),
            }

    for m in messages:
        sw = m.get("sensitive_words_found", [])
        if sw and isinstance(sw, list) and (len(sw) == 0 or isinstance(sw[0], str)):
            details: List[Dict[str, Any]] = []
            for w in sw:
                if not isinstance(w, str):
                    continue
                details.append(word_detail_map.get(w, {"word": w, "category": None, "subcategory": None, "severity": 1}))
            m["sensitive_words_found"] = details

    conversation["messages"] = messages
    return conversation

async def add_message(conversation_id: str, user_id: str, content: str) -> Dict[str, Any]:
    """
    添加用户消息并获取AI回复
    用途：写入用户消息，进行敏感词检测；如有敏感词，记录审计并返回拒绝回复；否则调用模型生成回复。
    入参：
        conversation_id: 对话ID
        user_id: 用户ID
        content: 用户消息内容
    返回：
        Dict: 包含处理结果的字典（含 contains_sensitive_words / sensitive_words_found / assistant_response）
    """
    # 预取对话用于判断是否首次消息与标题更新
    conversation = await db.db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": user_id
    })
    if not conversation:
        raise ValueError("对话不存在或无权限")

    is_first_message = len(conversation.get("messages", [])) == 0
    current_title = conversation.get("title", "")

    # 检查敏感词
    check_result = sensitive_word_filter.check_text(content)
    contains_sensitive = check_result["contains_sensitive_words"]
    sensitive_words = check_result["sensitive_words_found"]
    highest_severity = check_result["highest_severity"]

    # Dify 智能体二次过滤（仅当本地过滤通过时执行）
    if not contains_sensitive:
        dify_result = await dify_service.check_content_safety(content, user_id)
        if not dify_result["safe"]:
            contains_sensitive = True
            dify_reason = dify_result.get("reason", "智能体识别为不安全内容")
            dify_suggestion = dify_result.get("suggestion", "")
            highest_severity = 4  # 设定为较高严重程度
            
            # 构造一个虚拟的敏感词信息添加到列表
            # 注意：sensitive_words 是一个列表，我们需要确保它是可变的
            if sensitive_words is None:
                sensitive_words = []
            
            sensitive_words.append({
                "word": "智能体拦截",
                "category": "智能检测",
                "subcategory": dify_reason,
                "severity": 4,
                "extra_info": dify_suggestion
            })

    # 详细敏感词信息（用于响应与审计）
    detailed_words: List[Dict[str, Any]] = []
    if contains_sensitive and sensitive_words:
        # 新版过滤器已返回结构化信息，直接使用；兼容旧版字符串列表
        if isinstance(sensitive_words[0], dict):
            detailed_words = sensitive_words
        else:
            words_list = [w for w in sensitive_words if isinstance(w, str)]
            if words_list:
                cursor = db.db.sensitive_words.find({"word": {"$in": words_list}})
                async for doc in cursor:
                    detailed_words.append({
                        "word": doc.get("word"),
                        "category": doc.get("category"),
                        "subcategory": doc.get("subcategory"),
                        "severity": doc.get("severity", 1),
                    })
                known = set(dw["word"] for dw in detailed_words)
                for w in words_list:
                    if w not in known:
                        detailed_words.append({"word": w, "category": None, "subcategory": None, "severity": 1})

    # 创建用户消息（消息中也保存结构化敏感词列表，便于后续展示）
    user_message = {
        "role": "user",
        "content": content,
        "timestamp": datetime.now(),
        "contains_sensitive_words": contains_sensitive,
        "sensitive_words_found": detailed_words if contains_sensitive else [],
        "highest_severity": highest_severity
    }

    # 更新对话（写入用户消息与更新时间）
    await db.db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {"messages": user_message},
            "$set": {"updated_at": datetime.now()}
        }
    )

    # 首次用户消息或原标题以“新会话”开头时，用内容前20字更新标题
    if is_first_message or (current_title.startswith("新会话") if current_title else True):
        new_title = content.strip()[:20] or f"新会话 {datetime.now().strftime('%m-%d %H:%M')}"
        await db.db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"title": new_title, "updated_at": datetime.now()}}
        )

    # 如果包含敏感词，记录并返回拒绝回复
    if contains_sensitive:
        highest = highest_severity
        if detailed_words:
            highest = max([dw.get("severity", 1) for dw in detailed_words])

        # 创建敏感词记录（包含详细信息）
        sensitive_record = {
            "user_id": user_id,
            "conversation_id": ObjectId(conversation_id),
            "message_content": content,
            "sensitive_words_found": detailed_words,
            "highest_severity": highest,
            "timestamp": datetime.now()
        }

        await db.db.sensitive_records.insert_one(sensitive_record)
        
        # 创建系统回复
        assistant_message = {
            "role": "assistant",
            "content": "当前问题暂无法回答。",
            "timestamp": datetime.now(),
            "contains_sensitive_words": False,
            "sensitive_words_found": []
        }
        
        # 更新对话
        await db.db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": assistant_message},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return {
            "contains_sensitive_words": True,
            "sensitive_words_found": detailed_words,
            "assistant_response": "当前问题暂无法回答。"
        }

    # 获取对话历史（最多取最近10条）
    conversation = await db.db.conversations.find_one({"_id": ObjectId(conversation_id)})
    messages = conversation.get("messages", [])
    model_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages[-10:]
    ]

    # 调用模型生成回复
    assistant_response = await generate_response(model_messages)

    # 创建助手回复消息
    assistant_message = {
        "role": "assistant",
        "content": assistant_response,
        "timestamp": datetime.now(),
        "contains_sensitive_words": False,
        "sensitive_words_found": []
    }

    # 更新对话
    await db.db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {"messages": assistant_message},
            "$set": {"updated_at": datetime.now()}
        }
    )

    return {
        "contains_sensitive_words": False,
        "sensitive_words_found": [],
        "assistant_response": assistant_response
    }

async def get_user_conversations(user_id: str) -> List[Dict]:
    """获取用户的所有对话（列表优化）
    用途：返回用户的对话列表，统一 ID 字段与标题；为降低负载，仅返回最近一条消息。
    入参：
    - user_id: 用户ID
    返回：
    - 对话字典列表（每项仅含最近一条 messages）
    """
    conversations: List[Dict[str, Any]] = []
    cursor = db.db.conversations.find({"user_id": user_id}).sort("updated_at", -1)
    
    async for c in cursor:
        c_id = str(c["_id"])
        c_user_id = str(c["user_id"])        
        title = c.get("title") or f"新会话 {c.get('created_at', datetime.now()).strftime('%m-%d %H:%M')}"
        # 仅返回最近一条消息
        last_msg = c.get("messages", [])[-1:]  # 列表切片保证仍是 List
        # 结构化敏感词
        if last_msg:
            sw = last_msg[0].get("sensitive_words_found", [])
            if sw and isinstance(sw, list) and (len(sw) == 0 or isinstance(sw[0], str)):
                details: List[Dict[str, Any]] = []
                if sw:
                    cursor_sw = db.db.sensitive_words.find({"word": {"$in": sw}})
                    known: Dict[str, Dict[str, Any]] = {}
                    async for doc in cursor_sw:
                        known[doc.get("word")] = {
                            "word": doc.get("word"),
                            "category": doc.get("category"),
                            "subcategory": doc.get("subcategory"),
                            "severity": doc.get("severity", 1),
                        }
                    for w in sw:
                        details.append(known.get(w, {"word": w, "category": None, "subcategory": None, "severity": 1}))
                last_msg[0]["sensitive_words_found"] = details
        conversations.append({
            "id": c_id,
            "_id": c_id,
            "user_id": c_user_id,
            "title": title,
            "messages": last_msg,
            "created_at": c.get("created_at"),
            "updated_at": c.get("updated_at"),
        })
    
    return conversations

async def delete_conversation(conversation_id: str, user_id: str) -> bool:
    """删除用户对话并清理关联敏感记录
    用途：仅删除当前用户归属的对话；若删除成功，清理敏感审计记录。
    入参：
    - conversation_id: 对话ID
    - user_id: 用户ID
    返回：
    - 是否删除成功（True/False）
    """
    filter_cond = {"_id": ObjectId(conversation_id), "user_id": user_id}
    del_res = await db.db.conversations.delete_one(filter_cond)
    if del_res.deleted_count != 1:
        return False
    # 清理敏感记录
    await db.db.sensitive_records.delete_many({
        "conversation_id": ObjectId(conversation_id),
        "user_id": ObjectId(user_id)
    })
    return True
