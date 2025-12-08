from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Path, Body
from typing import List, Optional, Dict
from datetime import datetime
import json
import csv
import io
from app.api.deps import get_current_admin_user, require_edition_for_mode
from pydantic import BaseModel
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
router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class CreatedId(BaseModel):
    id: str

class ImportedCount(BaseModel):
    imported_count: int

@router.post(
    "/sensitive-words",
    response_model=CreatedId,
    status_code=status.HTTP_201_CREATED,
    summary="添加敏感词",
    description="新增敏感词，需管理员权限。",
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足，需要管理员权限"}}}},
    },
)
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

@router.post(
    "/sensitive-words/bulk",
    response_model=ImportedCount,
    status_code=status.HTTP_201_CREATED,
    summary="批量添加敏感词",
    description="批量新增敏感词，需管理员权限。",
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足，需要管理员权限"}}}},
    },
)
async def bulk_create_sensitive_words(
    words_data: SensitiveWordBulkImport,
    _: dict = Depends(get_current_admin_user)
):
    """批量添加敏感词（仅管理员）"""
    count = await bulk_import_sensitive_words(words_data.words)
    return {"imported_count": count}

@router.post(
    "/sensitive-words/import",
    status_code=status.HTTP_201_CREATED,
    response_model=ImportedCount,
    summary="从文件导入敏感词",
    description="支持CSV或JSON导入敏感词，需管理员权限。",
    responses={
        400: {"description": "文件格式错误", "content": {"application/json": {"example": {"detail": "仅支持CSV和JSON格式文件"}}}},
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足，需要管理员权限"}}}},
    },
)
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

@router.delete(
    "/sensitive-words/{word_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除敏感词",
    description="根据ID删除敏感词，需管理员权限。",
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足，需要管理员权限"}}}},
        404: {"description": "敏感词不存在", "content": {"application/json": {"example": {"detail": "敏感词不存在"}}}},
    },
)
async def remove_sensitive_word(
    word_id: str = Path(..., description="敏感词ID"),
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

@router.get(
    "/sensitive-words",
    response_model=List[SensitiveWordResponse],
    summary="查询敏感词",
    description="按条件查询敏感词列表，需管理员权限。",
)
async def list_sensitive_words(
    category: Optional[str] = Query(None, description="主分类"),
    subcategory: Optional[str] = Query(None, description="子分类"),
    min_severity: Optional[int] = Query(None, description="最小严重程度"),
    max_severity: Optional[int] = Query(None, description="最大严重程度"),
    _: dict = Depends(get_current_admin_user)
):
    return await get_all_sensitive_words(category, subcategory, min_severity, max_severity)

@router.get(
    "/sensitive-records",
    response_model=List[SensitiveRecordResponse],
    summary="查询敏感词记录",
    description="按条件筛选敏感词命中记录，需管理员权限。",
)
async def list_sensitive_records(
    user_id: Optional[str] = Query(None, description="用户ID"),
    conversation_id: Optional[str] = Query(None, description="对话ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    category: Optional[str] = Query(None, description="主分类"),
    subcategory: Optional[str] = Query(None, description="子分类"),
    min_severity: Optional[int] = Query(None, description="最小严重程度"),
    max_severity: Optional[int] = Query(None, description="最大严重程度"),
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

@router.get(
    "/categories",
    response_model=CategoriesResponse,
    summary="获取分类配置",
    description="获取当前所有敏感词分类配置，需管理员权限。",
)
async def list_categories(
    _: dict = Depends(get_current_admin_user)
):
    """获取所有敏感词分类（仅管理员）"""
    return {"categories": await get_categories()}

@router.get(
    "/categories/default",
    response_model=CategoriesResponse,
    summary="获取默认分类",
    description="获取默认的敏感词主分类及子分类配置，需管理员权限。",
)
async def get_default_categories(
    _: dict = Depends(get_current_admin_user)
):
    """获取默认敏感词分类（仅管理员）"""
    return {"categories": {cat: SENSITIVE_WORD_SUBCATEGORIES.get(cat, []) for cat in SENSITIVE_WORD_CATEGORIES}}

@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增分类",
    description="新增敏感词主分类及子分类配置，需管理员权限。",
    responses={
        400: {"description": "分类已存在", "content": {"application/json": {"example": {"detail": "分类已存在"}}}},
    },
)
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

@router.put(
    "/categories/{category_name}",
    response_model=CategoryResponse,
    summary="更新分类子项",
    description="更新指定主分类的子分类列表，需管理员权限。",
    responses={
        404: {"description": "分类不存在", "content": {"application/json": {"example": {"detail": "分类不存在"}}}},
    },
)
async def update_category_subcategories(
    category_name: str = Path(..., description="主分类名称"),
    subcategories: List[str] = Body(..., description="子分类列表"),
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

@router.delete(
    "/categories/{category_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除分类",
    description="删除指定主分类（默认分类不可删除），需管理员权限。",
    responses={
        404: {"description": "分类不存在或不可删除", "content": {"application/json": {"example": {"detail": "分类不存在或无法删除默认分类"}}}},
    },
)
async def remove_category(
    category_name: str = Path(..., description="主分类名称"),
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
