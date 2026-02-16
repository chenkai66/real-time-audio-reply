"""
测试 Token 计数工具
"""
import pytest
from backend.utils.token import TokenCounter, token_counter


class TestTokenCounter:
    """测试 TokenCounter 类"""
    
    def test_init(self):
        """测试初始化"""
        counter = TokenCounter()
        assert counter.encoding is not None
    
    def test_count_text_empty(self):
        """测试空文本"""
        counter = TokenCounter()
        assert counter.count_text("") == 0
        assert counter.count_text(None) == 0
    
    def test_count_text_english(self):
        """测试英文文本"""
        counter = TokenCounter()
        text = "Hello, world!"
        tokens = counter.count_text(text)
        assert tokens > 0
        assert tokens < len(text)  # token 数应该少于字符数
    
    def test_count_text_chinese(self):
        """测试中文文本"""
        counter = TokenCounter()
        text = "你好，世界！"
        tokens = counter.count_text(text)
        assert tokens > 0
    
    def test_count_messages_empty(self):
        """测试空消息列表"""
        counter = TokenCounter()
        messages = []
        tokens = counter.count_messages(messages)
        assert tokens == 2  # 只有结束 token
    
    def test_count_messages_single(self):
        """测试单条消息"""
        counter = TokenCounter()
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        tokens = counter.count_messages(messages)
        assert tokens > 0
    
    def test_count_messages_multiple(self):
        """测试多条消息"""
        counter = TokenCounter()
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
            {"role": "user", "content": "请介绍一下你自己"}
        ]
        tokens = counter.count_messages(messages)
        assert tokens > 10
    
    def test_estimate_tokens_english(self):
        """测试英文估算"""
        counter = TokenCounter()
        text = "This is a test sentence."
        estimated = counter.estimate_tokens(text)
        actual = counter.count_text(text)
        # 估算值应该在实际值的 50%-150% 范围内
        assert 0.5 * actual <= estimated <= 1.5 * actual
    
    def test_estimate_tokens_chinese(self):
        """测试中文估算"""
        counter = TokenCounter()
        text = "这是一个测试句子。"
        estimated = counter.estimate_tokens(text)
        actual = counter.count_text(text)
        # 估算值应该在实际值的 50%-150% 范围内
        assert 0.5 * actual <= estimated <= 1.5 * actual
    
    def test_estimate_tokens_mixed(self):
        """测试中英文混合估算"""
        counter = TokenCounter()
        text = "这是一个 test 句子 with mixed content。"
        estimated = counter.estimate_tokens(text)
        actual = counter.count_text(text)
        # 估算值应该在实际值的 50%-150% 范围内
        assert 0.5 * actual <= estimated <= 1.5 * actual
    
    def test_global_instance(self):
        """测试全局实例"""
        assert token_counter is not None
        tokens = token_counter.count_text("Test")
        assert tokens > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

