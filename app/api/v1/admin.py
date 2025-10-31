from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_current_admin_user
from app.schemas.sensitive_word import SensitiveWordCreate, SensitiveWordResponse, SensitiveRecordResponse
from app.services.sensitive_word import add_sensitive_word, delete_sensitive_word, get_all_sensitive_words, get_sensitive_records

router = APIRouter()

@router.post("/sensitive-words", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_sensitive_word(
    word_data: SensitiveWordCreate,
    _: dict = Depends(get_current_admin_user)
):
    """添加敏感词（仅管理员）"""
    word_id = await add_sensitive_word(word_data.word, word_data.category)
    return {"id": word_id}

@router.delete("/sensitive-words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_sensitive_word(
    word_id: str,
    _: dict = Depends(get_current_admin_user)
):
    """删除敏感词（仅管理员）"""
    success = await delete_sensitive_word(word_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="敏感词不存在"
        )
    return None

@router.get("/sensitive-words", response_model=List[SensitiveWordResponse])
async def list_sensitive_words(
    _: dict = Depends(get_current_admin_user)
):
    """获取所有敏感词（仅管理员）"""
    return await get_all_sensitive_words()

@router.get("/sensitive-records", response_model=List[SensitiveRecordResponse])
async def list_sensitive_records(
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    _: dict = Depends(get_current_admin_user)
):
    """获取敏感词记录（仅管理员）"""
    return await get_sensitive_records(user_id, start_date, end_date)