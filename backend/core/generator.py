"""
回复生成模块
基于大模型生成对学生提问的回复
"""
from typing import Optional, Dict, List
from backend.services.openai_service import openai_service
from backend.core.conversation import ConversationHistory
from backend.core.role import Role


class ReplyGenerator:
    """回复生成器"""
    
    def __init__(self, model: str = "qwen-plus"):
        """
        初始化回复生成器
        
        Args:
            model: 使用的模型名称
        """
        self.model = model
        self.system_prompt = """你是一位授课助手，负责回答学生在课堂上的提问。

要求：
1. 回答简洁明了，控制在 150 字以内
2. 使用通俗易懂的语言
3. 如果问题不清楚，礼貌地要求学生补充
4. 结合上下文给出针对性回答
5. 保持专业和友好的语气

注意：
- 不要回答与课程无关的问题
- 如果不确定答案，诚实地说明
- 鼓励学生独立思考"""
    
    async def generate(
        self,
        question: str,
        context: Optional[str] = None,
        conversation_history: Optional[ConversationHistory] = None,
        temperature: float = 0.7
    ) -> str:
        """
        生成回复
        
        Args:
            question: 学生的问题
            context: 额外的上下文信息
            conversation_history: 对话历史
            temperature: 温度参数
            
        Returns:
            生成的回复
        """
        if not openai_service:
            return "抱歉，AI 服务暂时不可用。"
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 添加对话历史上下文
        if conversation_history:
            history_context = conversation_history.get_context(max_tokens=2000)
            if history_context:
                messages.append({
                    "role": "system",
                    "content": f"对话历史：\n{history_context}"
                })
        
        # 添加额外上下文
        if context:
            messages.append({
                "role": "system",
                "content": f"当前上下文：\n{context}"
            })
        
        # 添加学生问题
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            response = await openai_service.chat_completion(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=300
            )
            
            return response["content"]
        except Exception as e:
            print(f"回复生成失败: {e}")
            return "抱歉，我暂时无法回答这个问题。请稍后再试。"
    
    async def generate_stream(
        self,
        question: str,
        context: Optional[str] = None,
        conversation_history: Optional[ConversationHistory] = None,
        temperature: float = 0.7
    ):
        """
        流式生成回复
        
        Args:
            question: 学生的问题
            context: 额外的上下文信息
            conversation_history: 对话历史
            temperature: 温度参数
            
        Yields:
            文本片段
        """
        if not openai_service:
            yield "抱歉，AI 服务暂时不可用。"
            return
        
        # 构建消息列表（同上）
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if conversation_history:
            history_context = conversation_history.get_context(max_tokens=2000)
            if history_context:
                messages.append({
                    "role": "system",
                    "content": f"对话历史：\n{history_context}"
                })
        
        if context:
            messages.append({
                "role": "system",
                "content": f"当前上下文：\n{context}"
            })
        
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            async for chunk in openai_service.chat_completion_stream(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=300
            ):
                yield chunk
        except Exception as e:
            print(f"流式回复生成失败: {e}")
            yield "抱歉，我暂时无法回答这个问题。"
    
    def is_valid_question(self, text: str) -> bool:
        """
        判断是否为有效问题
        
        Args:
            text: 文本内容
            
        Returns:
            是否为有效问题
        """
        # 过滤无效输入
        invalid_patterns = [
            "嗯", "啊", "哦", "好的", "知道了", "明白了",
            "谢谢", "好", "是的", "对", "没错"
        ]
        
        text_lower = text.lower().strip()
        
        # 太短的文本
        if len(text_lower) < 3:
            return False
        
        # 匹配无效模式
        if any(pattern in text_lower for pattern in invalid_patterns):
            return False
        
        # 包含问号或疑问词
        question_indicators = ["?", "？", "吗", "呢", "如何", "怎么", "为什么", "什么", "哪", "是否"]
        if any(indicator in text for indicator in question_indicators):
            return True
        
        # 默认认为是有效的（可能是陈述式问题）
        return True
    
    async def filter_and_generate(
        self,
        text: str,
        context: Optional[str] = None,
        conversation_history: Optional[ConversationHistory] = None
    ) -> Optional[str]:
        """
        过滤并生成回复
        
        Args:
            text: 学生的文本
            context: 上下文
            conversation_history: 对话历史
            
        Returns:
            生成的回复，如果不是有效问题则返回 None
        """
        if not self.is_valid_question(text):
            return None
        
        return await self.generate(text, context, conversation_history)


# 全局实例
reply_generator = ReplyGenerator()

