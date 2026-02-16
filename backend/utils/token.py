"""
Token 计数工具
使用 tiktoken 精确计算 token 数量
"""
import tiktoken
from typing import List, Dict


class TokenCounter:
    """Token 计数器"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        初始化 Token 计数器
        
        Args:
            model: 模型名称，用于选择对应的编码器
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # 如果模型不存在，使用默认编码器
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_text(self, text: str) -> int:
        """
        计算文本的 token 数量
        
        Args:
            text: 输入文本
            
        Returns:
            token 数量
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        计算消息列表的 token 数量
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            
        Returns:
            总 token 数量
        """
        total_tokens = 0
        
        for message in messages:
            # 每条消息的基础 token（role + 分隔符）
            total_tokens += 4
            
            for key, value in message.items():
                total_tokens += self.count_text(str(value))
                if key == "name":
                    total_tokens += -1  # role 已经计算过了
        
        # 每次对话的结束 token
        total_tokens += 2
        
        return total_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """
        快速估算 token 数量（不精确但更快）
        
        Args:
            text: 输入文本
            
        Returns:
            估算的 token 数量
        """
        # 粗略估算：中文约 1.5 字符/token，英文约 4 字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        
        return int(chinese_chars / 1.5 + other_chars / 4)


# 全局实例
token_counter = TokenCounter()

