"""
OpenAI 兼容接口服务
用于调用通义千问大模型
"""
from typing import List, Dict, Optional, AsyncIterator, Any
from openai import AsyncOpenAI
from config.settings import settings


class OpenAIService:
    """OpenAI 兼容接口服务"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化服务
        
        Args:
            api_key: API Key
            base_url: API 基础 URL
            model: 默认模型名称
        """
        self.api_key = api_key or settings.openai_api_key
        self.base_url = base_url or settings.openai_base_url
        self.model = model or settings.openai_model
        
        if not self.api_key:
            raise ValueError("OpenAI API Key is required")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否流式输出
            
        Returns:
            响应字典
        """
        model = model or self.model
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            return response
        
        return {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        """
        流式聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Yields:
            文本片段
        """
        model = model or self.model
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def simple_chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        简单聊天（单轮对话）
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示
            model: 模型名称
            temperature: 温度参数
            
        Returns:
            模型回复
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature
        )
        
        return response["content"]


# 全局实例
openai_service = OpenAIService() if settings.openai_api_key else None

