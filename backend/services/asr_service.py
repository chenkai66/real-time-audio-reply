"""
阿里云 DashScope 实时语音识别服务
"""
import asyncio
import json
import logging
from typing import Optional, Callable
import websockets
from websockets.client import WebSocketClientProtocol
import os

logger = logging.getLogger(__name__)


class DashScopeASR:
    """阿里云 DashScope 实时语音识别"""
    
    def __init__(self, api_key: str = None):
        """
        初始化 ASR 服务
        
        Args:
            api_key: DashScope API Key
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 未设置")
        
        # WebSocket 连接
        self.ws: Optional[WebSocketClientProtocol] = None
        self.is_connected = False
        
        # 配置（使用 Realtime API）
        self.url = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
        self.model = "qwen3-asr-flash-realtime"  # 千问实时语音识别
        
        # 回调函数
        self.on_result: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # 状态
        self.task_id: Optional[str] = None
        self.is_running = False
    
    async def connect(self):
        """建立 WebSocket 连接"""
        try:
            logger.info(f"正在连接 DashScope Realtime API: {self.model}")
            
            # Realtime API URL 格式：需要同时传递 api_key 和 model
            url_with_params = f"{self.url}?api_key={self.api_key}&model={self.model}"
            
            # 建立连接
            self.ws = await websockets.connect(
                url_with_params,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.is_connected = True
            logger.info("✅ DashScope ASR 连接成功")
            
            # 启动接收任务
            asyncio.create_task(self._receive_loop())
            
        except Exception as e:
            logger.error(f"❌ DashScope ASR 连接失败: {e}")
            self.is_connected = False
            raise
    
    async def start_recognition(self, sample_rate: int = 16000):
        """
        开始识别（使用 Realtime API）
        
        Args:
            sample_rate: 采样率（Hz）
        """
        if not self.is_connected:
            await self.connect()
        
        # 配置会话（Realtime API 格式）
        session_config = {
            "type": "session.update",
            "session": {
                "model": self.model,  # 指定模型
                "modalities": ["text"],  # 只需要文本输出
                "transcription": {
                    "language": "zh",  # 中文
                    "input_audio_format": "pcm",
                    "input_sample_rate": sample_rate
                }
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        self.is_running = True
        logger.info("✅ 开始识别")
    
    async def send_audio(self, audio_data: bytes):
        """
        发送音频数据（Realtime API 格式）
        
        Args:
            audio_data: PCM 音频数据（16-bit）
        """
        if not self.is_connected or not self.is_running:
            logger.warning("ASR 未连接或未启动")
            return
        
        try:
            # Realtime API 需要 base64 编码
            import base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 发送音频数据
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64
            }
            
            await self.ws.send(json.dumps(audio_message))
        except Exception as e:
            logger.error(f"发送音频失败: {e}")
            if self.on_error:
                await self.on_error(str(e))
    
    async def stop_recognition(self):
        """停止识别"""
        if not self.is_running:
            return
        
        # 发送结束消息（Realtime API）
        stop_message = {
            "type": "session.finish"
        }
        
        await self.ws.send(json.dumps(stop_message))
        self.is_running = False
        logger.info("✅ 停止识别")
    
    async def _receive_loop(self):
        """接收消息循环"""
        try:
            async for message in self.ws:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("ASR 连接已关闭")
            self.is_connected = False
        except Exception as e:
            logger.error(f"接收消息错误: {e}")
            if self.on_error:
                await self.on_error(str(e))
    
    async def _handle_message(self, message: str):
        """
        处理接收到的消息（Realtime API 格式）
        
        Args:
            message: JSON 消息
        """
        try:
            data = json.loads(message)
            event_type = data.get("type")
            
            # 处理不同类型的事件
            if event_type == "session.created":
                # 会话创建
                session_id = data.get("session", {}).get("id")
                logger.info(f"会话创建: {session_id}")
            
            elif event_type == "session.updated":
                # 会话配置更新
                logger.info("会话配置已更新")
            
            elif event_type == "input_audio_buffer.speech_started":
                # VAD 检测到语音开始
                logger.info("======VAD 检测到语音开始======")
            
            elif event_type == "input_audio_buffer.speech_stopped":
                # VAD 检测到语音结束
                logger.info("======VAD 检测到语音结束======")
            
            elif event_type == "conversation.item.input_audio_transcription.text":
                # 中间识别结果
                text = data.get("text", "")
                if text and self.on_result:
                    await self.on_result({
                        "text": text,
                        "is_final": False,
                        "confidence": 1.0
                    })
            
            elif event_type == "conversation.item.input_audio_transcription.completed":
                # 最终识别结果
                text = data.get("transcript", "")
                if text and self.on_result:
                    await self.on_result({
                        "text": text,
                        "is_final": True,
                        "confidence": 1.0
                    })
                logger.info(f"识别完成: {text}")
            
            elif event_type == "error":
                # 错误
                error_message = data.get("error", {}).get("message", "未知错误")
                logger.error(f"ASR 错误: {error_message}")
                if self.on_error:
                    await self.on_error(error_message)
            
            else:
                logger.debug(f"未处理的事件: {event_type}")
        
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    async def disconnect(self):
        """断开连接"""
        if self.is_running:
            await self.stop_recognition()
        
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        self.is_connected = False
        logger.info("✅ ASR 已断开")
    
    def set_result_callback(self, callback: Callable):
        """设置识别结果回调"""
        self.on_result = callback
    
    def set_error_callback(self, callback: Callable):
        """设置错误回调"""
        self.on_error = callback


class ASRService:
    """ASR 服务管理器（支持多用户）"""
    
    def __init__(self):
        self.sessions = {}  # user_id -> DashScopeASR
    
    async def create_session(self, user_id: str) -> DashScopeASR:
        """
        为用户创建 ASR 会话
        
        Args:
            user_id: 用户ID
        
        Returns:
            DashScopeASR 实例
        """
        if user_id in self.sessions:
            logger.warning(f"用户 {user_id} 已有 ASR 会话")
            return self.sessions[user_id]
        
        asr = DashScopeASR()
        await asr.connect()
        self.sessions[user_id] = asr
        
        logger.info(f"✅ 为用户 {user_id} 创建 ASR 会话")
        return asr
    
    async def remove_session(self, user_id: str):
        """
        移除用户的 ASR 会话
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.sessions:
            asr = self.sessions[user_id]
            await asr.disconnect()
            del self.sessions[user_id]
            logger.info(f"✅ 移除用户 {user_id} 的 ASR 会话")
    
    def get_session(self, user_id: str) -> Optional[DashScopeASR]:
        """
        获取用户的 ASR 会话
        
        Args:
            user_id: 用户ID
        
        Returns:
            DashScopeASR 实例或 None
        """
        return self.sessions.get(user_id)
    
    async def cleanup(self):
        """清理所有会话"""
        for user_id in list(self.sessions.keys()):
            await self.remove_session(user_id)


# 全局 ASR 服务实例
asr_service = ASRService()

