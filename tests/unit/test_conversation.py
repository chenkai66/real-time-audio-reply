"""
测试对话历史管理模块
"""
import pytest
from datetime import datetime
from backend.core.conversation import (
    ConversationTurn,
    ConversationSummary,
    ConversationHistory
)
from backend.core.role import Role


class TestConversationTurn:
    """测试 ConversationTurn 类"""
    
    def test_init(self):
        """测试初始化"""
        turn = ConversationTurn(
            role=Role.TEACHER,
            text="Hello",
            timestamp=datetime.now(),
            tokens=5
        )
        assert turn.role == Role.TEACHER
        assert turn.text == "Hello"
        assert turn.tokens == 5
    
    def test_to_dict(self):
        """测试转换为字典"""
        turn = ConversationTurn(
            role=Role.STUDENT,
            text="Question?",
            timestamp=datetime.now(),
            tokens=3
        )
        d = turn.to_dict()
        assert d["role"] == "student"
        assert d["text"] == "Question?"
        assert d["tokens"] == 3
        assert "timestamp" in d


class TestConversationSummary:
    """测试 ConversationSummary 类"""
    
    def test_init(self):
        """测试初始化"""
        summary = ConversationSummary(
            original_turns=5,
            summary_text="Summary",
            key_points=["point1", "point2"],
            tokens=10,
            timestamp=datetime.now()
        )
        assert summary.original_turns == 5
        assert summary.summary_text == "Summary"
        assert len(summary.key_points) == 2
    
    def test_to_dict(self):
        """测试转换为字典"""
        summary = ConversationSummary(
            original_turns=3,
            summary_text="Test",
            key_points=["a"],
            tokens=5,
            timestamp=datetime.now()
        )
        d = summary.to_dict()
        assert d["original_turns"] == 3
        assert d["summary_text"] == "Test"
        assert "timestamp" in d


class TestConversationHistory:
    """测试 ConversationHistory 类"""
    
    def test_init(self):
        """测试初始化"""
        history = ConversationHistory()
        assert history.l1_size == 2
        assert history.l2_size == 3
        assert history.compression_threshold == 3000
        assert len(history.l1_cache) == 0
        assert history.total_tokens == 0
    
    def test_add_turn(self):
        """测试添加对话"""
        history = ConversationHistory()
        history.add_turn(Role.TEACHER, "Hello, class!")
        
        assert len(history.l1_cache) == 1
        assert history.total_turns == 1
        assert history.total_tokens > 0
    
    def test_add_multiple_turns(self):
        """测试添加多个对话"""
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "Welcome to the class.")
        history.add_turn(Role.STUDENT, "Thank you, teacher.")
        history.add_turn(Role.TEACHER, "Let's begin.")
        
        assert len(history.l1_cache) == 3
        assert history.total_turns == 3
    
    def test_get_context_empty(self):
        """测试获取空上下文"""
        history = ConversationHistory()
        context = history.get_context()
        assert context == ""
    
    def test_get_context_with_turns(self):
        """测试获取有内容的上下文"""
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "Hello")
        history.add_turn(Role.STUDENT, "Hi")
        
        context = history.get_context()
        assert "教师" in context
        assert "学生" in context
        assert "Hello" in context
        assert "Hi" in context
    
    def test_get_context_with_token_limit(self):
        """测试带 token 限制的上下文获取"""
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "This is a long sentence with many words.")
        history.add_turn(Role.STUDENT, "Short.")
        
        # 限制很小的 token 数
        context = history.get_context(max_tokens=5)
        # 应该只包含最新的短对话
        assert "Short" in context
    
    def test_get_recent_questions(self):
        """测试获取最近的问题"""
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "Today's topic is Python.")
        history.add_turn(Role.STUDENT, "What is Python?")
        history.add_turn(Role.TEACHER, "Python is a programming language.")
        history.add_turn(Role.STUDENT, "How do I install it?")
        
        questions = history.get_recent_questions(limit=2)
        assert len(questions) == 2
        assert "How do I install it?" in questions
        assert "What is Python?" in questions
    
    def test_get_recent_questions_limit(self):
        """测试问题数量限制"""
        history = ConversationHistory()
        
        for i in range(10):
            history.add_turn(Role.STUDENT, f"Question {i}?")
        
        questions = history.get_recent_questions(limit=3)
        assert len(questions) == 3
    
    def test_clear(self):
        """测试清空历史"""
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "Hello")
        history.add_turn(Role.STUDENT, "Hi")
        
        history.clear()
        
        assert len(history.l1_cache) == 0
        assert len(history.l2_cache) == 0
        assert history.total_tokens == 0
        assert history.total_turns == 0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "Hello")
        history.add_turn(Role.STUDENT, "Hi")
        
        stats = history.get_stats()
        assert stats["total_turns"] == 2
        assert stats["total_tokens"] > 0
        assert stats["l1_size"] == 2
        assert "l1_tokens" in stats
    
    def test_create_simple_summary(self):
        """测试创建简单摘要"""
        history = ConversationHistory()
        
        turns = [
            ConversationTurn(Role.TEACHER, "Hello", datetime.now(), 5),
            ConversationTurn(Role.STUDENT, "Hi", datetime.now(), 3)
        ]
        
        summary = history._create_simple_summary(turns)
        assert "教师" in summary
        assert "学生" in summary
        assert isinstance(summary, str)
    
    def test_compression_trigger(self):
        """测试压缩触发（需要大量数据）"""
        history = ConversationHistory(l1_size=2, compression_threshold=100)
        
        # 添加足够多的对话触发压缩
        for i in range(10):
            history.add_turn(Role.TEACHER, f"This is a long sentence number {i} with many words to increase token count.")
            history.add_turn(Role.STUDENT, f"Question {i}?")
        
        # 应该触发了压缩
        # L1 应该只保留最新的 2 轮
        assert len(history.l1_cache) <= 2 * 2  # 2轮 * 2条消息


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

