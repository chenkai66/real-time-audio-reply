"""
DashScope 服务封装
提供语音识别和大模型调用功能
"""
import asyncio
import json
from typing import Optional, Callable, Dict, Any
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
import dashscope
from config.settings import settings


class ASRCallback(RecognitionCallback):
    """ASR 回调处理器"""
    
    def __init__(
        self,
        on_sentence: Optional[Callable[[str, bool], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[], None]] = None
    ):
        """
        初始化回调处理器
        
        Args:
            on_sentence: 句子回调，参数为 (text, is_final)
            on_error: 错误回调，参数为 error_message
            on_complete: 完成回调
        """
        self.on_sentence_callback = on_sentence
        self.on_error_callback = on_error
        self.on_complete_callback = on_complete
        self.current_text = ""
    
    def on_event(self, result: RecognitionResult) -> None:
        """处理识别事件"""
        sentence = result.get_sentence()
        if sentence and 'text' in sentence:
            text = sentence['text']
            is_final = sentence.get('is_final', False)
            
            if self.on_sentence_callback:
                self.on_sentence_callback(text, is_final)
            
            if is_final:
                self.current_text = text
    
    def on_complete(self) -> None:
        """识别完成"""
        if self.on_complete_callback:
            self.on_complete_callback()
    
    def on_error(self, result: RecognitionResult) -> None:
        """处理错误"""
        error_msg = result.message if hasattr(result, 'message') else "Unknown error"
        if self.on_error_callback:
            self.on_error_callback(error_msg)
    
    def on_open(self) -> None:
        """连接打开"""
        pass
    
    def on_close(self) -> None:
        """连接关闭"""
        pass


class DashScopeService:
    """DashScope 服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化服务
        
        Args:
            api_key: API Key，如果不提供则从配置读取
        """
        self.api_key = api_key or settings.dashscope_api_key
        if not self.api_key:
            raise ValueError("DashScope API Key is required")
        
        dashscope.api_key = self.api_key
        self.recognition: Optional[Recognition] = None
        self.is_running = False
    
    def create_recognition(
        self,
        model: str = "paraformer-realtime-v2",
        format: str = "pcm",
        sample_rate: int = 16000,
        callback: Optional[ASRCallback] = None
    ) -> Recognition:
        """
        创建语音识别实例
        
        Args:
            model: 模型名称
            format: 音频格式
            sample_rate: 采样率
            callback: 回调处理器
            
        Returns:
            Recognition 实例
        """
        if not callback:
            callback = ASRCallback()
        
        recognition = Recognition(
            model=model,
            format=format,
            sample_rate=sample_rate,
            callback=callback
        )
        
        return recognition
    
    async def start_recognition(
        self,
        on_sentence: Optional[Callable[[str, bool], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
        model: str = "paraformer-realtime-v2"
    ) -> Recognition:
        """
        启动语音识别
        
        Args:
            on_sentence: 句子回调
            on_error: 错误回调
            on_complete: 完成回调
            model: 模型名称
            
        Returns:
            Recognition 实例
        """
        callback = ASRCallback(
            on_sentence=on_sentence,
            on_error=on_error,
            on_complete=on_complete
        )
        
        self.recognition = self.create_recognition(
            model=model,
            callback=callback
        )
        
        # 在线程池中启动（因为 dashscope SDK 是同步的）
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.recognition.start)
        
        self.is_running = True
        return self.recognition
    
    async def send_audio(self, audio_data: bytes) -> None:
        """
        发送音频数据
        
        Args:
            audio_data: PCM 音频数据
        """
        if not self.recognition or not self.is_running:
            raise RuntimeError("Recognition not started")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.recognition.send_audio_frame, audio_data)
    
    async def stop_recognition(self) -> None:
        """停止语音识别"""
        if self.recognition and self.is_running:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.recognition.stop)
            self.is_running = False


# 全局实例
dashscope_service = DashScopeService() if settings.dashscope_api_key else None

