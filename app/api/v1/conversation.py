from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_active_user
from app.schemas.conversation import MessageCreate, ConversationResponse
from app.services.conversation import create_conversation, get_conversation, add_message, get_user_conversations

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_conversation(current_user: dict = Depends(get_current_active_user)):
    """创建新对话"""
    conversation_id = await create_conversation(str(current_user["_id"]))
    return {"id": conversation_id}

@router.get("/", response_model=list)
async def list_conversations(current_user: dict = Depends(get_current_active_user)):
    """获取用户的所有对话"""
    conversations = await get_user_conversations(str(current_user["_id"]))
    return conversations

@router.get("/{conversation_id}", response_model=dict)
async def get_single_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """获取单个对话"""
    conversation = await get_conversation(conversation_id, str(current_user["_id"]))
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    return conversation

@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """发送消息并获取回复"""
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