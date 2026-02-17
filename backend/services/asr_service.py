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
        
        # 配置
        self.url = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
        self.model = "paraformer-realtime-v2"  # 高准确率模型
        # self.model = "fun-asr-realtime"  # 低延迟模型（可选）
        
        # 回调函数
        self.on_result: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # 状态
        self.task_id: Optional[str] = None
        self.is_running = False
    
    async def connect(self):
        """建立 WebSocket 连接"""
        try:
            logger.info(f"正在连接 DashScope ASR: {self.model}")
            
            # 建立连接
            self.ws = await websockets.connect(
                self.url,
                extra_headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
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
        开始识别
        
        Args:
            sample_rate: 采样率（Hz）
        """
        if not self.is_connected:
            await self.connect()
        
        # 发送开始识别消息
        start_message = {
            "header": {
                "action": "start-recognition",
                "streaming": "duplex",
                "task_id": None  # 服务器会分配
            },
            "payload": {
                "model": self.model,
                "parameters": {
                    "format": "pcm",
                    "sample_rate": sample_rate,
                    "enable_vad": True,  # 启用 VAD
                    "enable_punctuation": True,  # 启用标点
                    "enable_inverse_text_normalization": True,  # 数字转换
                    "max_sentence_silence": 800,  # 句子间最大静音（ms）
                    "enable_intermediate_result": True,  # 启用中间结果
                }
            }
        }
        
        await self.ws.send(json.dumps(start_message))
        self.is_running = True
        logger.info("✅ 开始识别")
    
    async def send_audio(self, audio_data: bytes):
        """
        发送音频数据
        
        Args:
            audio_data: PCM 音频数据（16-bit）
        """
        if not self.is_connected or not self.is_running:
            logger.warning("ASR 未连接或未启动")
            return
        
        try:
            # 发送音频数据（二进制）
            await self.ws.send(audio_data)
        except Exception as e:
            logger.error(f"发送音频失败: {e}")
            if self.on_error:
                await self.on_error(str(e))
    
    async def stop_recognition(self):
        """停止识别"""
        if not self.is_running:
            return
        
        # 发送停止消息
        stop_message = {
            "header": {
                "action": "stop-recognition",
                "task_id": self.task_id
            }
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
        处理接收到的消息
        
        Args:
            message: JSON 消息
        """
        try:
            data = json.loads(message)
            header = data.get("header", {})
            payload = data.get("payload", {})
            
            # 获取 task_id
            if not self.task_id and header.get("task_id"):
                self.task_id = header["task_id"]
                logger.info(f"Task ID: {self.task_id}")
            
            # 处理不同类型的消息
            event = header.get("event")
            
            if event == "recognition-started":
                logger.info("识别已开始")
            
            elif event == "recognition-result-changed":
                # 中间结果（实时显示）
                result = payload.get("result", {})
                text = result.get("text", "")
                if text and self.on_result:
                    await self.on_result({
                        "text": text,
                        "is_final": False,
                        "confidence": result.get("confidence", 0)
                    })
            
            elif event == "recognition-completed":
                # 最终结果
                result = payload.get("result", {})
                text = result.get("text", "")
                if text and self.on_result:
                    await self.on_result({
                        "text": text,
                        "is_final": True,
                        "confidence": result.get("confidence", 0)
                    })
                logger.info(f"识别完成: {text}")
            
            elif event == "error":
                # 错误
                error_message = payload.get("message", "未知错误")
                logger.error(f"ASR 错误: {error_message}")
                if self.on_error:
                    await self.on_error(error_message)
            
            else:
                logger.debug(f"未处理的事件: {event}")
        
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

