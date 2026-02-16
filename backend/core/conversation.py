"""
对话历史管理模块
实现三层缓存策略（L1/L2/L3）
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from backend.utils.token import token_counter
from backend.services.openai_service import openai_service
from backend.core.role import Role


@dataclass
class ConversationTurn:
    """对话轮次"""
    role: Role
    text: str
    timestamp: datetime
    tokens: int
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "role": self.role.value,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "tokens": self.tokens
        }


@dataclass
class ConversationSummary:
    """对话摘要"""
    original_turns: int
    summary_text: str
    key_points: List[str]
    tokens: int
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "original_turns": self.original_turns,
            "summary_text": self.summary_text,
            "key_points": self.key_points,
            "tokens": self.tokens,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationHistory:
    """对话历史管理器"""
    
    def __init__(
        self,
        l1_size: int = 2,
        l2_size: int = 3,
        compression_threshold: int = 3000
    ):
        """
        初始化对话历史管理器
        
        Args:
            l1_size: L1 缓存大小（完整保留的轮数）
            l2_size: L2 缓存大小（摘要保留的轮数）
            compression_threshold: 压缩阈值（token 数）
        """
        self.l1_cache: List[ConversationTurn] = []  # 最近的完整对话
        self.l2_cache: List[ConversationSummary] = []  # 压缩的摘要
        self.l3_index: List[Dict] = []  # 历史问题索引
        
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.compression_threshold = compression_threshold
        
        self.total_tokens = 0
        self.total_turns = 0
    
    def add_turn(self, role: Role, text: str) -> None:
        """
        添加对话轮次
        
        Args:
            role: 角色
            text: 对话内容
        """
        tokens = token_counter.count_text(text)
        turn = ConversationTurn(
            role=role,
            text=text,
            timestamp=datetime.now(),
            tokens=tokens
        )
        
        self.l1_cache.append(turn)
        self.total_tokens += tokens
        self.total_turns += 1
        
        # 检查是否需要压缩
        if self.total_tokens > self.compression_threshold:
            self._trigger_compression()
    
    def _trigger_compression(self) -> None:
        """触发压缩（同步版本，实际应该异步）"""
        # 如果 L1 缓存超过限制，将旧的对话移到 L2
        while len(self.l1_cache) > self.l1_size:
            # 取出最旧的对话
            turns_to_compress = self.l1_cache[:self.l1_size]
            self.l1_cache = self.l1_cache[self.l1_size:]
            
            # 创建摘要（这里先用简单的文本拼接，后续会用大模型）
            summary_text = self._create_simple_summary(turns_to_compress)
            summary_tokens = token_counter.count_text(summary_text)
            
            summary = ConversationSummary(
                original_turns=len(turns_to_compress),
                summary_text=summary_text,
                key_points=[],
                tokens=summary_tokens,
                timestamp=datetime.now()
            )
            
            self.l2_cache.append(summary)
            
            # 更新 token 计数
            original_tokens = sum(t.tokens for t in turns_to_compress)
            self.total_tokens = self.total_tokens - original_tokens + summary_tokens
        
        # 如果 L2 缓存超过限制，将旧的摘要移到 L3
        while len(self.l2_cache) > self.l2_size:
            old_summary = self.l2_cache.pop(0)
            
            # 提取问题到 L3 索引
            for turn in self.l1_cache:
                if turn.role == Role.STUDENT and "?" in turn.text or "吗" in turn.text:
                    self.l3_index.append({
                        "question": turn.text,
                        "timestamp": turn.timestamp.isoformat()
                    })
            
            self.total_tokens -= old_summary.tokens
    
    def _create_simple_summary(self, turns: List[ConversationTurn]) -> str:
        """
        创建简单摘要（不调用大模型）
        
        Args:
            turns: 对话轮次列表
            
        Returns:
            摘要文本
        """
        summary_parts = []
        for turn in turns:
            role_name = "教师" if turn.role == Role.TEACHER else "学生"
            # 截断过长的文本
            text = turn.text[:50] + "..." if len(turn.text) > 50 else turn.text
            summary_parts.append(f"{role_name}: {text}")
        
        return " | ".join(summary_parts)
    
    async def create_ai_summary(self, turns: List[ConversationTurn]) -> ConversationSummary:
        """
        使用 AI 创建高质量摘要
        
        Args:
            turns: 对话轮次列表
            
        Returns:
            对话摘要
        """
        if not openai_service:
            # 如果没有 AI 服务，使用简单摘要
            summary_text = self._create_simple_summary(turns)
            return ConversationSummary(
                original_turns=len(turns),
                summary_text=summary_text,
                key_points=[],
                tokens=token_counter.count_text(summary_text),
                timestamp=datetime.now()
            )
        
        # 构建对话文本
        conversation_text = "\n".join([
            f"{'教师' if t.role == Role.TEACHER else '学生'}: {t.text}"
            for t in turns
        ])
        
        system_prompt = """你是一个对话摘要助手。请将以下对话压缩为简洁的摘要，保留：
1. 主要讨论的主题
2. 学生提出的关键问题
3. 重要的知识点

摘要应该简洁明了，控制在 100 字以内。"""
        
        try:
            summary_text = await openai_service.simple_chat(
                prompt=conversation_text,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            return ConversationSummary(
                original_turns=len(turns),
                summary_text=summary_text,
                key_points=[],
                tokens=token_counter.count_text(summary_text),
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"AI 摘要生成失败: {e}")
            # 降级到简单摘要
            summary_text = self._create_simple_summary(turns)
            return ConversationSummary(
                original_turns=len(turns),
                summary_text=summary_text,
                key_points=[],
                tokens=token_counter.count_text(summary_text),
                timestamp=datetime.now()
            )
    
    def get_context(self, max_tokens: Optional[int] = None) -> str:
        """
        获取用于大模型的上下文
        
        Args:
            max_tokens: 最大 token 数限制
            
        Returns:
            上下文文本
        """
        context_parts = []
        current_tokens = 0
        
        # 首先添加 L1 缓存（最新的完整对话）
        for turn in reversed(self.l1_cache):
            if max_tokens and current_tokens + turn.tokens > max_tokens:
                break
            
            role_name = "教师" if turn.role == Role.TEACHER else "学生"
            context_parts.insert(0, f"{role_name}: {turn.text}")
            current_tokens += turn.tokens
        
        # 如果还有空间，添加 L2 缓存（摘要）
        if not max_tokens or current_tokens < max_tokens:
            for summary in reversed(self.l2_cache):
                if max_tokens and current_tokens + summary.tokens > max_tokens:
                    break
                
                context_parts.insert(0, f"[历史摘要]: {summary.summary_text}")
                current_tokens += summary.tokens
        
        return "\n".join(context_parts)
    
    def get_recent_questions(self, limit: int = 5) -> List[str]:
        """
        获取最近的学生问题
        
        Args:
            limit: 返回数量限制
            
        Returns:
            问题列表
        """
        questions = []
        
        # 从 L1 缓存中提取问题
        for turn in reversed(self.l1_cache):
            if turn.role == Role.STUDENT:
                questions.append(turn.text)
                if len(questions) >= limit:
                    break
        
        return questions
    
    def clear(self) -> None:
        """清空所有历史"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l3_index.clear()
        self.total_tokens = 0
        self.total_turns = 0
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_turns": self.total_turns,
            "total_tokens": self.total_tokens,
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "l3_size": len(self.l3_index),
            "l1_tokens": sum(t.tokens for t in self.l1_cache),
            "l2_tokens": sum(s.tokens for s in self.l2_cache)
        }


# 全局实例
conversation_history = ConversationHistory()

