from typing import List, Set, Dict, Tuple, Any
from app.db.mongodb import db

class TrieNode:
    """Trie树节点，用于敏感词匹配"""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.word_info = None  # 存储敏感词的完整信息

import hashlib
import json
import redis.asyncio as redis
from app.core.config import settings

class SensitiveWordFilter:
    def __init__(self):
        self.root = TrieNode()
        self.sensitive_words = {}  # 改为字典，存储敏感词及其信息
        
        # 初始化 Redis 连接
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        
    async def load_sensitive_words(self):
        """从数据库加载敏感词"""
        self.sensitive_words = {}
        self.root = TrieNode()
        
        # 从数据库获取敏感词
        cursor = db.db.sensitive_words.find({})
        async for document in cursor:
            word = document.get("word", "")
            if word:
                # 提取敏感词的完整信息
                word_info = {
                    "id": str(document.get("_id")),
                    "word": word,
                    "category": document.get("category"),
                    "subcategory": document.get("subcategory"),
                    "severity": document.get("severity", 1)
                }
                self.sensitive_words[word] = word_info
                self._add_to_trie(word, word_info)
    
    def _add_to_trie(self, word: str, word_info: Dict[str, Any]):
        """将敏感词添加到Trie树中，并存储其完整信息"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.word_info = word_info
    
    async def check_text(self, text: str) -> Dict[str, Any]:
        """
        检查文本是否包含敏感词 (优先查询 Redis 缓存)
        
        Args:
            text: 要检查的文本
            
        Returns:
            Dict[str, Any]: {
                "contains_sensitive_words": bool,
                "sensitive_words_found": List[Dict],
                "highest_severity": int
            }
        """
        if not text:
            return {
                "contains_sensitive_words": False,
                "sensitive_words_found": [],
                "highest_severity": 0
            }
            
        # 1. 尝试从 Redis 获取缓存结果
        cache_key = f"filter_cache:{hashlib.md5(text.encode('utf-8')).hexdigest()}"
        try:
            cached_result = await self.redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        except Exception as e:
            # Redis 异常不应阻塞业务，降级为直接计算
            pass
        
        found_words = []
        highest_severity = 0
        text_lower = text.lower()  # 转为小写进行匹配
        
        # 遍历文本的每个字符作为起点
        for i in range(len(text_lower)):
            node = self.root
            for j in range(i, len(text_lower)):
                char = text_lower[j]
                
                # 如果字符不在当前节点的子节点中，结束当前匹配
                if char not in node.children:
                    break
                
                node = node.children[char]
                
                # 如果到达某个敏感词的结尾
                if node.is_end_of_word and node.word_info:
                    # 使用原始敏感词信息
                    word_info = node.word_info.copy()
                    found_words.append(word_info)
                    
                    # 更新最高严重程度
                    severity = word_info.get("severity", 1)
                    if severity > highest_severity:
                        highest_severity = severity
                    
                    break
        
        result = {
            "contains_sensitive_words": len(found_words) > 0,
            "sensitive_words_found": found_words,
            "highest_severity": highest_severity
        }
        
        # 2. 将计算结果写入 Redis 缓存 (过期时间 1 小时)
        try:
            await self.redis_client.setex(cache_key, 3600, json.dumps(result))
        except Exception:
            pass
            
        return result

# 创建全局敏感词过滤器实例
sensitive_word_filter = SensitiveWordFilter()