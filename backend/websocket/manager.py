"""
WebSocket 连接管理器
处理音频数据传输和实时通信
"""
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            "connected_at": datetime.now().isoformat(),
            "audio_buffer": [],
            "is_processing": False
        }
        
        await self.send_message(user_id, {
            "type": "connected",
            "message": "连接成功",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"用户 {user_id} 已连接")
    
    async def disconnect(self, user_id: str):
        """断开连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        logger.info(f"用户 {user_id} 已断开")
    
    async def send_message(self, user_id: str, message: dict):
        """发送消息给指定用户"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                await self.disconnect(user_id)
    
    async def broadcast(self, message: dict):
        """广播消息给所有用户"""
        for user_id in list(self.active_connections.keys()):
            await self.send_message(user_id, message)
    
    async def send_status(self, user_id: str, status: str, message: str = ""):
        """发送状态更新"""
        await self.send_message(user_id, {
            "type": "status",
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_transcript(self, user_id: str, text: str, role: str):
        """发送转写结果"""
        await self.send_message(user_id, {
            "type": "transcript",
            "text": text,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_reply(self, user_id: str, text: str):
        """发送回复"""
        await self.send_message(user_id, {
            "type": "reply",
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_error(self, user_id: str, error_message: str):
        """发送错误消息"""
        await self.send_message(user_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_session(self, user_id: str) -> Optional[dict]:
        """获取用户会话"""
        return self.user_sessions.get(user_id)
    
    def is_connected(self, user_id: str) -> bool:
        """检查用户是否连接"""
        return user_id in self.active_connections


# 全局连接管理器实例
manager = ConnectionManager()

