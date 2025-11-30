from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.deps import get_current_active_user, require_edition_for_mode
from app.schemas.conversation import (
    MessageCreate,
    ConversationDocOut,
    ConversationResponse,
    CreatedId,
    MessageSendResult,
    DeleteResult,
)
from app.services.conversation import (
    create_conversation,
    get_conversation,
    add_message,
    get_user_conversations,
    delete_conversation,
)

# 在路由层挂载版别运行模式依赖，限制仅允许当前模式的用户访问
router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CreatedId)
async def create_new_conversation(current_user: dict = Depends(get_current_active_user)):
    """创建新对话（返回新建 ID）
    用途：为当前用户新建会话，并返回新会话的 ID。
    依赖：鉴权用户、版别运行模式。
    """
    conversation_id = await create_conversation(str(current_user["_id"]))
    return {"id": conversation_id}

@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(current_user: dict = Depends(get_current_active_user)):
    """获取用户的所有对话（列表优化）
    用途：返回当前用户的对话列表，统一字段并降低负载（仅最近一条消息）。
    """
    conversations = await get_user_conversations(str(current_user["_id"]))
    return conversations

@router.get("/{conversation_id}", response_model=ConversationDocOut)
async def get_single_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """获取单个对话详情
    用途：返回指定对话的完整消息列表，统一 ID 与标题字段。
    """
    conversation = await get_conversation(conversation_id, str(current_user["_id"]))
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    return conversation

@router.delete("/{conversation_id}", response_model=DeleteResult)
async def remove_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """删除对话
    用途：仅允许删除当前用户归属的对话，并清理关联敏感记录。
    返回：删除结果（deleted: bool）
    """
    ok = await delete_conversation(conversation_id, str(current_user["_id"]))
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在或无权限")
    return {"deleted": True, "message": "删除成功"}

@router.post("/{conversation_id}/messages", response_model=MessageSendResult)
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """发送消息并获取回复
    用途：在指定对话中发送用户消息；若命中敏感词返回拒绝回复并记录；否则返回模型生成的助手回复。
    """
    # 检查对话是否存在
    conversation = await get_conversation(conversation_id, str(current_user["_id"]))
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 添加消息并获取回复
    result = await add_message(conversation_id, str(current_user["_id"]), message.content)
    
    return result