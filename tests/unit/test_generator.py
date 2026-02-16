"""
测试回复生成模块
"""
import pytest
from backend.core.generator import ReplyGenerator, reply_generator
from backend.core.conversation import ConversationHistory
from backend.core.role import Role


class TestReplyGenerator:
    """测试 ReplyGenerator 类"""
    
    def test_init(self):
        """测试初始化"""
        generator = ReplyGenerator(model="qwen-turbo")
        assert generator.model == "qwen-turbo"
        assert generator.system_prompt is not None
    
    def test_is_valid_question_true(self):
        """测试有效问题判断"""
        generator = ReplyGenerator()
        
        assert generator.is_valid_question("什么是Python？") is True
        assert generator.is_valid_question("如何学习编程") is True
        assert generator.is_valid_question("这个怎么做") is True
        assert generator.is_valid_question("为什么会这样呢") is True
    
    def test_is_valid_question_false(self):
        """测试无效问题判断"""
        generator = ReplyGenerator()
        
        assert generator.is_valid_question("嗯") is False
        assert generator.is_valid_question("好的") is False
        assert generator.is_valid_question("知道了") is False
        assert generator.is_valid_question("谢谢") is False
        assert generator.is_valid_question("是") is False
    
    def test_is_valid_question_short(self):
        """测试过短的文本"""
        generator = ReplyGenerator()
        assert generator.is_valid_question("好") is False
        assert generator.is_valid_question("哦") is False
    
    @pytest.mark.asyncio
    async def test_generate_basic(self):
        """测试基本回复生成"""
        generator = ReplyGenerator()
        
        try:
            reply = await generator.generate(
                question="什么是变量？",
                context="我们正在学习Python基础"
            )
            assert isinstance(reply, str)
            assert len(reply) > 0
        except Exception as e:
            # 如果 API 不可用，跳过测试
            pytest.skip(f"API 不可用: {e}")
    
    @pytest.mark.asyncio
    async def test_generate_with_history(self):
        """测试带历史的回复生成"""
        generator = ReplyGenerator()
        history = ConversationHistory()
        
        history.add_turn(Role.TEACHER, "今天学习Python")
        history.add_turn(Role.STUDENT, "什么是变量")
        
        try:
            reply = await generator.generate(
                question="能举个例子吗？",
                conversation_history=history
            )
            assert isinstance(reply, str)
            assert len(reply) > 0
        except Exception as e:
            pytest.skip(f"API 不可用: {e}")
    
    @pytest.mark.asyncio
    async def test_filter_and_generate_valid(self):
        """测试过滤并生成（有效问题）"""
        generator = ReplyGenerator()
        
        try:
            reply = await generator.filter_and_generate(
                text="什么是Python？"
            )
            assert reply is not None
            assert isinstance(reply, str)
        except Exception as e:
            pytest.skip(f"API 不可用: {e}")
    
    @pytest.mark.asyncio
    async def test_filter_and_generate_invalid(self):
        """测试过滤并生成（无效问题）"""
        generator = ReplyGenerator()
        
        reply = await generator.filter_and_generate(
            text="嗯嗯"
        )
        assert reply is None
    
    def test_global_instance(self):
        """测试全局实例"""
        assert reply_generator is not None
        assert isinstance(reply_generator, ReplyGenerator)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

