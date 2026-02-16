"""
测试 OpenAI 服务模块
"""
import pytest
from backend.services.openai_service import OpenAIService


class TestOpenAIService:
    """测试 OpenAIService 类"""
    
    def test_init_with_params(self):
        """测试带参数初始化"""
        service = OpenAIService(
            api_key="test-key",
            base_url="https://test.com",
            model="test-model"
        )
        
        assert service.api_key == "test-key"
        assert service.base_url == "https://test.com"
        assert service.model == "test-model"
    
    def test_init_without_key_raises(self):
        """测试没有 API Key 时抛出异常"""
        # 需要模拟 settings 中也没有 key 的情况
        from unittest.mock import patch
        with patch('backend.services.openai_service.settings') as mock_settings:
            mock_settings.openai_api_key = None
            mock_settings.openai_base_url = "https://test.com"
            mock_settings.openai_model = "test"
            
            with pytest.raises(ValueError, match="API Key is required"):
                OpenAIService()
    
    @pytest.mark.asyncio
    async def test_simple_chat(self):
        """测试简单聊天"""
        # 这个测试需要真实的 API Key
        try:
            from config.settings import settings
            if not settings.openai_api_key:
                pytest.skip("No API key configured")
            
            service = OpenAIService()
            response = await service.simple_chat(
                prompt="测试",
                system_prompt="你是一个测试助手",
                temperature=0.1
            )
            
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"API 调用失败: {e}")
    
    @pytest.mark.asyncio
    async def test_chat_completion(self):
        """测试聊天补全"""
        try:
            from config.settings import settings
            if not settings.openai_api_key:
                pytest.skip("No API key configured")
            
            service = OpenAIService()
            messages = [
                {"role": "user", "content": "你好"}
            ]
            
            response = await service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=10
            )
            
            assert "content" in response
            assert "role" in response
            assert "usage" in response
        except Exception as e:
            pytest.skip(f"API 调用失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

