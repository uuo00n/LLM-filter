from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
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

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedId,
    summary="创建对话",
    description="为当前用户新建会话，返回新建的会话ID。",
    responses={
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def create_new_conversation(current_user: dict = Depends(get_current_active_user)):
    conversation_id = await create_conversation(str(current_user["_id"]))
    return {"id": conversation_id}

@router.get(
    "/",
    response_model=List[ConversationResponse],
    summary="获取对话列表",
    description="返回当前用户的对话列表（包含最近一条消息等精简信息）。",
    responses={
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def list_conversations(current_user: dict = Depends(get_current_active_user)):
    conversations = await get_user_conversations(str(current_user["_id"]))
    return conversations

@router.get(
    "/{conversation_id}",
    response_model=ConversationDocOut,
    summary="获取对话详情",
    description="返回指定对话的完整消息列表。",
    responses={
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        404: {"description": "对话不存在", "content": {"application/json": {"example": {"detail": "对话不存在"}}}},
    },
)
async def get_single_conversation(
    conversation_id: str = Path(..., description="对话ID"),
    current_user: dict = Depends(get_current_active_user)
):
    conversation = await get_conversation(conversation_id, str(current_user["_id"]))
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    return conversation

@router.delete(
    "/{conversation_id}",
    response_model=DeleteResult,
    summary="删除对话",
    description="删除当前用户归属的指定对话。",
    responses={
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        404: {"description": "对话不存在或无权限", "content": {"application/json": {"example": {"detail": "对话不存在或无权限"}}}},
    },
)
async def remove_conversation(
    conversation_id: str = Path(..., description="对话ID"),
    current_user: dict = Depends(get_current_active_user)
):
    ok = await delete_conversation(conversation_id, str(current_user["_id"]))
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在或无权限")
    return {"deleted": True, "message": "删除成功"}

@router.post(
    "/{conversation_id}/messages",
    response_model=MessageSendResult,
    summary="发送消息并获取回复",
    description="向指定对话发送消息，返回助手回复或敏感词拒绝信息。",
    responses={
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        404: {"description": "对话不存在", "content": {"application/json": {"example": {"detail": "对话不存在"}}}},
    },
)
async def send_message(
    conversation_id: str = Path(..., description="对话ID"),
    message: MessageCreate = Body(..., description="消息内容"),
    current_user: dict = Depends(get_current_active_user)
):
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
