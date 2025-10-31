from typing import List, Set, Dict, Tuple
from app.db.mongodb import db

class TrieNode:
    """Trie树节点，用于敏感词匹配"""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class SensitiveWordFilter:
    def __init__(self):
        self.root = TrieNode()
        self.sensitive_words = set()
        
    async def load_sensitive_words(self):
        """从数据库加载敏感词"""
        self.sensitive_words = set()
        self.root = TrieNode()
        
        # 从数据库获取敏感词
        cursor = db.db.sensitive_words.find({})
        async for document in cursor:
            word = document.get("word", "")
            if word:
                self.sensitive_words.add(word)
                self._add_to_trie(word)
    
    def _add_to_trie(self, word: str):
        """将敏感词添加到Trie树中"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def check_text(self, text: str) -> Tuple[bool, List[str]]:
        """
        检查文本是否包含敏感词
        
        Args:
            text: 要检查的文本
            
        Returns:
            Tuple[bool, List[str]]: (是否包含敏感词, 找到的敏感词列表)
        """
        if not text:
            return False, []
        
        found_words = []
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
                if node.is_end_of_word:
                    word = text_lower[i:j+1]
                    found_words.append(word)
                    break
        
        return len(found_words) > 0, found_words

# 创建全局敏感词过滤器实例
sensitive_word_filter = SensitiveWordFilter()