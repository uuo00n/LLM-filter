from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List, Optional, Dict
from datetime import datetime
import json
import csv
import io
from app.api.deps import get_current_admin_user
from app.schemas.sensitive_word import (
    SensitiveWordCreate, SensitiveWordResponse, SensitiveRecordResponse,
    SensitiveWordBulkImport, CategoryCreate, CategoryResponse, CategoriesResponse
)
from app.services.sensitive_word import (
    add_sensitive_word, delete_sensitive_word, get_all_sensitive_words, 
    get_sensitive_records, get_categories, add_category, update_category,
    delete_category, bulk_import_sensitive_words
)
from app.models.sensitive_word import SENSITIVE_WORD_CATEGORIES, SENSITIVE_WORD_SUBCATEGORIES

router = APIRouter()

@router.post("/sensitive-words", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_sensitive_word(
    word_data: SensitiveWordCreate,
    _: dict = Depends(get_current_admin_user)
):
    """添加敏感词（仅管理员）"""
    word_id = await add_sensitive_word(
        word_data.word, 
        word_data.category, 
        word_data.subcategory, 
        word_data.severity
    )
    return {"id": word_id}

@router.post("/sensitive-words/bulk", response_model=dict, status_code=status.HTTP_201_CREATED)
async def bulk_create_sensitive_words(
    words_data: SensitiveWordBulkImport,
    _: dict = Depends(get_current_admin_user)
):
    """批量添加敏感词（仅管理员）"""
    count = await bulk_import_sensitive_words(words_data.words)
    return {"imported_count": count}

@router.post("/sensitive-words/import", status_code=status.HTTP_201_CREATED)
async def import_sensitive_words_from_file(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_admin_user)
):
    """从文件导入敏感词（仅管理员）
    
    支持CSV和JSON格式:
    - CSV格式: word,category,subcategory,severity
    - JSON格式: 包含word, category, subcategory, severity字段的对象数组
    """
    content = await file.read()
    words = []
    
    if file.filename.endswith('.csv'):
        # 处理CSV文件
        csv_content = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_content)
        for row in reader:
            severity = int(row.get('severity', 1)) if row.get('severity') else 1
            words.append(SensitiveWordCreate(
                word=row['word'],
                category=row['category'],
                subcategory=row.get('subcategory'),
                severity=severity
            ))
    elif file.filename.endswith('.json'):
        # 处理JSON文件
        data = json.loads(content)
        for item in data:
            words.append(SensitiveWordCreate(
                word=item['word'],
                category=item['category'],
                subcategory=item.get('subcategory'),
                severity=item.get('severity', 1)
            ))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持CSV和JSON格式文件"
        )
    
    count = await bulk_import_sensitive_words(words)
    return {"imported_count": count}

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
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    min_severity: Optional[int] = None,
    max_severity: Optional[int] = None,
    _: dict = Depends(get_current_admin_user)
):
    """获取所有敏感词（仅管理员）
    
    可选筛选参数:
    - category: 主分类
    - subcategory: 子分类
    - min_severity: 最小严重程度
    - max_severity: 最大严重程度
    """
    return await get_all_sensitive_words(category, subcategory, min_severity, max_severity)

@router.get("/sensitive-records", response_model=List[SensitiveRecordResponse])
async def list_sensitive_records(
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    min_severity: Optional[int] = None,
    max_severity: Optional[int] = None,
    _: dict = Depends(get_current_admin_user)
):
    """获取敏感词记录（仅管理员）
    
    可选筛选参数:
    - user_id: 用户ID
    - conversation_id: 对话ID
    - start_date: 开始日期
    - end_date: 结束日期
    - category: 主分类
    - subcategory: 子分类
    - min_severity: 最小严重程度
    - max_severity: 最大严重程度
    """
    return await get_sensitive_records(
        user_id, conversation_id, start_date, end_date,
        category, subcategory, min_severity, max_severity
    )

@router.get("/categories", response_model=CategoriesResponse)
async def list_categories(
    _: dict = Depends(get_current_admin_user)
):
    """获取所有敏感词分类（仅管理员）"""
    return {"categories": await get_categories()}

@router.get("/categories/default", response_model=CategoriesResponse)
async def get_default_categories(
    _: dict = Depends(get_current_admin_user)
):
    """获取默认敏感词分类（仅管理员）"""
    return {"categories": {cat: SENSITIVE_WORD_SUBCATEGORIES.get(cat, []) for cat in SENSITIVE_WORD_CATEGORIES}}

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    _: dict = Depends(get_current_admin_user)
):
    """添加敏感词分类（仅管理员）"""
    success = await add_category(category_data.name, category_data.subcategories)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类已存在"
        )
    return {"name": category_data.name, "subcategories": category_data.subcategories}

@router.put("/categories/{category_name}", response_model=CategoryResponse)
async def update_category_subcategories(
    category_name: str,
    subcategories: List[str],
    _: dict = Depends(get_current_admin_user)
):
    """更新敏感词分类的子分类（仅管理员）"""
    success = await update_category(category_name, subcategories)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    return {"name": category_name, "subcategories": subcategories}

@router.delete("/categories/{category_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(
    category_name: str,
    _: dict = Depends(get_current_admin_user)
):
    """删除敏感词分类（仅管理员）"""
    success = await delete_category(category_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在或无法删除默认分类"
        )
    return None